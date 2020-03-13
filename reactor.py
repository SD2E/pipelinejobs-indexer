import os
import sys
import traceback
import json
import logging
from attrdict import AttrDict
from jsonschema import ValidationError
from pprint import pprint
from urllib.parse import unquote

from reactors.runtime import Reactor, agaveutils
from datacatalog.managers.pipelinejobs import ManagedPipelineJobInstance
from datacatalog.managers.pipelinejobs import ManagedPipelineJobError


def minify_job_dict(post_dict):
    """Strip out extraneous keys from an Agave job POST

    Returns:
        dict: Slim, svelte job dictionary
    """
    for strip_key in ["_links", "retries", "localId"]:
        if strip_key in post_dict:
            del post_dict[strip_key]
    return post_dict


def forward_event(uuid, event, state, data={}, robj=None):
    # Propagate non-index events to events-manager via message
    # jobs-indexer needs to implement propagation for itself to ensure that
    # job terminal state is captured and sent along correctly
    try:
        handled_event_body = {
            'job_uuid': uuid,
            'event_name': event,
            'job_state': state,
            'data': data
        }
        resp = robj.send_message('events-manager.prod',
                                 handled_event_body,
                                 retryMaxAttempts=3)
        return True
    except Exception as exc:
        robj.logger.warning(
            "Failed to propagate handled({0}) for {1}: {2}".format(
                event, uuid, exc))


def main():

    rx = Reactor()
    mes = AttrDict(rx.context.message_dict)

    if mes == {}:
        try:
            jsonmsg = json.loads(rx.context.raw_message)
            mes = jsonmsg
        except Exception:
            pass

    #    ['event', 'agavejobs', 'index', 'indexed']
    action = "urlparams"
    try:
        for a in ["index", "indexed"]:
            try:
                rx.logger.debug("Checking against schema {}".format(a))
                rx.validate_message(mes,
                                    messageschema="/schemas/" + a +
                                    ".jsonschema",
                                    permissive=False)
                action = a
                break
            except Exception as exc:
                print("Validation error: {}".format(exc))
        if action is None:
            pprint(mes)
            raise ValidationError("Unknown schema")
    except Exception as vexc:
        rx.on_failure("Message was not processed", vexc)

    rx.logger.debug("Schema: {}".format(action))

    # for k, v in os.environ.items():
    #     rx.logger.debug("env:{}={}".format(k, v))

    PARAMS = [
        ("uuid", "uuid", None),
        ("token", "token", None),
        ("level", "level", "1"),
        ("filters", "filters", None),
    ]

    # Look in the message, then in context, then in environment for values
    cb = dict()
    try:
        for param, key, default in PARAMS:
            cb[key] = mes.get(
                param, rx.context.get(param, os.environ.get(param, default)))
            rx.logger.debug("param:{}={}".format(param, cb[key]))
    except Exception as exc:
        rx.on_failure(exc)
    # Transform JSON string representation of filters so they can be used
    # as Python regex. This is enough for filters passed from message but
    # not a URL parameter.
    # TODO implement urldecode on ?filters parameter
    parsed_filters = cb["filters"]
    # if cb["filters"] is not None:
    #     for f in cb["filters"]:
    #         parsed_filters.append(unquote(f))
    #     cb["filters"] = parsed_filters

    # Simple case - we're just processing 'indexed'
    if action == "indexed":
        try:
            store = ManagedPipelineJobInstance(rx.settings.mongodb,
                                               cb["uuid"],
                                               agave=rx.client)
            resp = store.indexed(token=cb["token"])

            # notify events manager that we processed an 'indexed' event
            forward_event(cb['uuid'], 'indexed', 'FINISHED', {}, rx)
            rx.on_success('Processed indexed event for {0}'.format(cb['uuid']))
        except Exception as mexc:
            rx.on_failure('Failed to handle indexed event: {}', mexc)

    if action in ["index", "urlparams"]:
        rx.logger.info('Indexing job {}'.format(cb['uuid']))
        try:
            store = ManagedPipelineJobInstance(rx.settings.mongodb,
                                               agave=rx.client,
                                               uuid=cb['uuid'])
            # TODO - Pass in generated_by=config#pipelines.process_uuid

            # notify events manager that we got an 'index' event
            forward_event(cb['uuid'], 'index', 'INDEXING', {}, rx)

            resp = store.index(
                token=cb["token"],
                transition=False,
                filters=cb["filters"],
                generated_by=[rx.settings.pipelines.process_uuid],
            )

            # rx.logger.info('store.index response was: {}'.format(resp))

            if isinstance(resp, list):
                rx.logger.info(
                    "Indexed {} files to PipelineJob {}. ({} usec)".format(
                        len(resp), cb["uuid"], rx.elapsed()))

                # Send 'indexed' event to job via PipelineJobsManager (not PipelineJobsIndexer!)
                # This results in two messages required to move a job to FINISHED from INDEXING
                # but allows the jobs-manager to subscribe to and acto on the indexed event
                try:
                    # resp = store.indexed(token=cb["token"])
                    job_manager_id = rx.settings.pipelines.job_manager_id
                    mgr_mes = {
                        'uuid': cb['uuid'],
                        'name': 'indexed',
                        'data': {
                            'source': 'jobs-manager.prod'
                        }
                    }
                    rx.send_message(job_manager_id, mgr_mes)

                    rx.on_success('Sent indexed event for {0}'.format(
                        cb['uuid']))
                except Exception as mexc:
                    rx.on_failure('Failed to send indexed event', mexc)
            else:
                rx.logger.info("Indexed and transitioned to {0}".format(
                    resp.get("state", "Unknown")))
        except Exception as iexc:
            rx.on_failure("Failed to accomplish indexing", iexc)
    else:
        rx.on_failure("Failed to interpret indexing request")


if __name__ == "__main__":
    main()
