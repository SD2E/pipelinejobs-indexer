PIPELINE JOBS INDEXER
=====================

This Abaco actor indexes ManagedPipelineJob archive paths. It works in synergy
with other actors that create jobs using the ``ManagedPipelineJob`` class from
``python-datacatalog``. It accepts one type of JSON message via authenticated
HTTP POST, which causes the indexing to take place.

How to Index a Job
------------------

The job indexing request must include the *uuid* for the originating job and
an authorization token issued when the job was created. It may also include
two optional parameters. The first is ``level`` which indicates the
**processing level** for the files indexed to this job. The second is
``filters`` which is a list of **url-encoded** Python regular expressions
that are used to subselect files in the job's archive path for indexing. The
default behavior if not ``filters`` are provided at all is for all files
in the archive path to be set as ``generated_by`` the particular job.

POST an index message
^^^^^^^^^^^^^^^^^^^^^

Text

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

One may pass ``uuid``, ``level``, and ``token`` as URL parameters in lieu of
POSTING them as a message. The ``filters`` key is not currently supported by
this method.

.. code-block:: shell

    curl -XPOST \
        https://<tenantUrl>/actors/v2/<actorId>/messages?uuid=1073f4ff-c2b9-5190-bd9a-e6a406d9796a&\
        level=1&token=0dc73dc3ff39b49a

Authentication
^^^^^^^^^^^^^^

All POSTs to a ``PipelineJobsIndexer`` must be authenticated. There are two
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
