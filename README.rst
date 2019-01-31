====================
PipelineJobs Indexer
====================

This Reactor indexes the contents of **ManagedPipelineJob** archive paths. It
implements two actions: **index** and **indexed**. It is normally run
automatically via **PipelineJobs Manager** when a job enters the **FINISHED**
state, but can also be activated on its own.

Index a Job
-----------

**PipelineJobs Indexer** can receive an **index** request via:

#. A JSON-formatted **pipelinejob_index** document
#. URL parameters that replicate a **pipelinejob_index** document

Here are the critical fields to request indexing:

1. ``uuid`` ID for job to be indexed (must validate as a known job)
2. ``name`` This is always **index**
3. ``token`` The job's update token (optional for now)
4. ``level`` The processing level for output files (default: **1**)
5. ``filters`` List of **url-encoded** Python regex that select a subset of ``archive_path``

Index Request as JSON
^^^^^^^^^^^^^^^^^^^^^

This message will index outputs of job ``1079f67e-0ef6-52fe-b4e9-d77875573860`` as
level "2" products, sub-selecting only files matching ``sample\.uw_biofab\.141715`` and ``sample-uw_biofab-141715``.

.. code-block:: json

    {
        "uuid": "1079f67e-0ef6-52fe-b4e9-d77875573860",
        "name": "index",
        "filters": [
            "sample%5C.uw_biofab%5C.141715",
            "sample-uw_biofab-141715"
        ],
        "level": "2",
        "token": "0dc73dc3ff39b49a"
    }

Index Request as URL Params
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    curl -XPOST \
        https://<tenantUrl>/actors/v2/<actorId>/messages?uuid=1073f4ff-c2b9-5190-bd9a-e6a406d9796a&\
        level=2&token=0dc73dc3ff39b49a&name=index --data '{"filters": ["sample.uw_biofab.141715", "sample-uw_biofab-141715"]}'

.. note:: Remember that ``filters`` cannot currently be passed as URL parameters.

Mark as Indexed
---------------

**PipelineJobs Indexer** can receive an **index** request via JSON message
or URL parameters. Here is an example.

.. code-block:: json

    {
        "uuid": "1079f67e-0ef6-52fe-b4e9-d77875573860",
        "name": "indexed",
        "token": "0dc73dc3ff39b49a"
    }

**PipelineJobs Indexer** sends itself an **indexed** message after completing
an indexing action. Thus, it is not usually necessary to send one manually and
in fact, should be avoided. Documentation on the **indexed** event is included
here mostly for the sake of completeness.

Authentication
--------------

POSTs to a **PipelineJobs Indexer** must be authenticated by one of two means:

  1. Send a valid TACC.cloud Oauth2 Bearer token with the request
  2. Include a special URL parameter called a **nonce** with the HTTP request

JSON Schemas
------------

.. literalinclude:: schemas/index.jsonschema
   :language: json
   :linenos:
   :caption: pipelinejob_index

.. literalinclude:: schemas/indexed.jsonschema
   :language: json
   :linenos:
   :caption: pipelinejob_indexed
