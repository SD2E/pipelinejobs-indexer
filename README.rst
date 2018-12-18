PIPELINE JOBS INDEXER
=====================

This Abaco actor that manages indexing of ManagedPipelineJob archive paths. It
works in synergy with other Abaco actors that create jobs using the
``ManagedPipelineJob`` class from ``python-datacatalog``. It accepts one type
of JSON message via authenticated HTTP POST, which causes the indexing to
take place.

Indexing a Job
--------------

Text

Use Case 1
^^^^^^^^^^

Text

.. code-block:: json

    {
      "uuid": "1073f4ff-c2b9-5190-bd9a-e6a406d9796a",
      "data": {
        "arbitrary": "key value data"
      },
      "name": "finish",
      "token": "0dc73dc3ff39b49a"
    }

Use Case 2
^^^^^^^^^^

Text

.. code-block:: shell

    curl -XPOST --data '{"arbitrary": "key value data"}' \
        https://<tenantUrl>/actors/v2/<actorId>/messages?uuid=1073f4ff-c2b9-5190-bd9a-e6a406d9796a&\
        event=finish&token=0dc73dc3ff39b49a


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
        name=finish&token=0dc73dc3ff39b49a&\
        x-nonce=TACC_XXXXxxxxYz
