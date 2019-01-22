PIPELINE JOBS INDEXER
=====================

This Abaco actor indexes the contents of ManagedPipelineJob
archive paths. It works in synergy with other actors that manage jobs
via the ``ManagedPipelineJob``. It accepts a JSON message with one
schema via authenticated HTTP POST, which causes the indexing to
begin, assuming the job is in a valid state for indexing.

Manually Indexing a Job
-----------------------

**PipelineJobsManager** attempts to automatically start an indexing
task when a job enters the ``FINISHED`` state. Indexing can
also be requested manually. To accomplish this, craft a message with
the following values:

1. ``uuid`` - the job to be indexed
2. ``token`` - the job's unique update token
3. ``level`` - the processing level for the **file** record
4. ``filters`` - a list of **url-encoded** Python regular expressions to select a subset of the contents of ``archive_path``

Send it to *PipelineJobsIndexer** via HTTP POST.

POST an index message
^^^^^^^^^^^^^^^^^^^^^

Here is an example message to index outputs from job ``1079f67e-0ef6-52fe-b4e9-d77875573860`` as
level "1" products, sub-selecting only files matching ``sample\.uw_biofab\.141715`` and ``sample-uw_biofab-141715``.

.. code-block:: json

    {
        "uuid": "1079f67e-0ef6-52fe-b4e9-d77875573860",
        "filters": [
            "sample%5C.uw_biofab%5C.141715",
            "sample-uw_biofab-141715"
        ],
        "level": "1",
        "token": "0dc73dc3ff39b49a"
    }

.. note: The job ``state`` must be ``FINISHED`` or later for indexing.

POST URL parameters
^^^^^^^^^^^^^^^^^^^

Values for ``uuid``, ``level``, and ``token`` may be passed as URL parameters
in lieu of including them in the POST message. Due to the complexity of URL-
encoding regular expressions, the ``filters`` key is not currently supported by
this approach.

.. code-block:: shell

    curl -XPOST \
        https://<tenantUrl>/actors/v2/<actorId>/messages?uuid=1073f4ff-c2b9-5190-bd9a-e6a406d9796a&\
        level=1&token=0dc73dc3ff39b49a

Authentication
^^^^^^^^^^^^^^

All POSTs to **PipelineJobsIndexer** must be authenticated. There are two
mechanisms by which this can happen:

  1. Send a valid TACC.cloud Oauth2 Bearer token with the request
  2. Include a special URL parameter called a **nonce** with the HTTP request

.. code-block:: shell
   :caption: "Sending a Bearer Token"

    curl -XPOST -H "Authorization: Bearer 969d11396c43b0b810387e4da840cb37" \
        --data '{"uuid": "1073f4ff-c2b9-5190-bd9a-e6a406d9796a", \
        "token": "0dc73dc3ff39b49a",\
        "name": "finish"}' \
        https://<tenantUrl>/actors/v2/<actorId>/messages

.. code-block:: shell
   :caption: "Using a Nonce"

    curl -XPOST --data '{"arbitrary": "key value data"}' \
        https://<tenantUrl>/actors/v2/<actorId>/messages?uuid=1073f4ff-c2b9-5190-bd9a-e6a406d9796a&\
        level=1&token=0dc73dc3ff39b49a&\
        x-nonce=TACC_XXXXxxxxYz
