import os
import sys
import json
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
    for strip_key in ['_links', 'retries', 'localId']:
        if strip_key in post_dict:
            del post_dict[strip_key]
    return post_dict

def main():

    rx = Reactor()
    mes = AttrDict(rx.context.message_dict)

    if mes == {}:
        try:
            jsonmsg = json.loads(rx.context.raw_message)
            mes = jsonmsg
        except Exception:
            pass

#    ['event', 'agavejobs', 'create', 'delete']
    action = 'urlparams'
    try:
        for a in ['index']:
            try:
                rx.logger.info('Testing against {} schema'.format(a))
                rx.validate_message(
                    mes, messageschema='/schemas/' + a + '.jsonschema', permissive=False)
                action = a
                break
            except Exception as exc:
                print('Validation error: {}'.format(exc))
        if action is None:
            pprint(mes)
            raise ValidationError('Message not a known schema')
    except Exception as vexc:
        rx.on_failure('Failed to process message', vexc)

    rx.logger.debug('SCHEMA DETECTED: {}'.format(action))

    PARAMS = [('event', 'event', 'index'),
              ('uuid', 'uuid', None),
              ('token', 'token', None),
              ('level', 'level', '1'),
              ('filters', 'filters', None)]

    cb = dict()
    for param, key, default in PARAMS:
        cb[key] = rx.context.get(param, mes.get(param, default))

    parameters = dict()
    if cb['level'] is not None:
        parameters['processing_level'] = cb['level']
    # TODO implement urldecode on ?filters parameter
    parsed_filters = list()
    if cb['filters'] is not None:
        for f in cb['filters']:
            parsed_filters.append(unquote(f))
        parameters['filters'] = parsed_filters

    if action in ['index', 'urlparams']:
        try:
            store = ManagedPipelineJobInstance(rx.settings.mongodb, cb['uuid'], agave=rx.client)
            resp = store.index_archive_path(filters=cb['filters'], processing_level=cb['level'])
            if isinstance(resp, list):
                rx.on_success('Indexed {} files to PipelineJob {}. ({} usec)'.format(len(resp), cb['uuid'], rx.elapsed()))

                # Send 'indexed' event to job via PipelineJobsManager
                try:
                    job_manager_id = rx.settings.pipelines.job_manager_id
                    mgr_mes = {'uuid': cb['uuid'], 'name': 'indexed'}
                    rx.send_message(job_manager_id, mgr_mes)
                except Exception as mexc:
                    rx.logger.warning(
                        'Failed to send "indexed" event to job {}: {}'.format(
                            cb['uuid', mexc]))

        except Exception as iexc:
            rx.on_failure('Failed to complete indexing', iexc)
    else:
        rx.on_failure('Failed to interpret request as indexing request')

if __name__ == '__main__':
    main()
