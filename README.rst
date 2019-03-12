====================
PipelineJobs Indexer
====================

This Reactor indexes the contents of **ManagedPipelineJob** archive paths. It
implements two actions: **index** and **indexed**. It is normally run
automatically via **PipelineJobs Manager** when a job enters the **FINISHED**
state, but can also be activated on its own.

Aliases
-------
Rather than track Abaco actorIds, various versions of this Reactor are
available using  Abaco's new *aliases* feature.

+-------------+-----------------------------------------+
| Version     | Alias                                   |
+=============+=========================================+
| Production  | ``jobs-indexer.prod``, ``jobs-indexer`` |
+-------------+-----------------------------------------+
| Staging     | NA                                      |
+-------------+-----------------------------------------+
| Development |``jobs-indexer.dev``                     |
+-------------+-----------------------------------------+

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
level "1" products, sub-selecting only files matching ``.bam`` and ``.sam`.

.. code-block:: json

    {
        "uuid": "1079f67e-0ef6-52fe-b4e9-d77875573860",
        "name": "index",
        "filters": [
            {"level":"1","patterns":[".bam$",".sam$"]}
        ],
        "level": "1",
        "token": "0dc73dc3ff39b49a"
    }

The message could be sent this using curl:

.. code-block:: shell

    curl -XPOST \
        https://<tenantUrl>/actors/v2/jobs-indexer.prg/messages?token=0dc73dc3ff39b49a --data '{"uuid":"1079f67e-0ef6-52fe-b4e9-d77875573860","name":"index","filters":[{"level":"1","patterns":[".bam$",".sam$"]}],"level":"1"}'

Or using the Abaco CLI like so:

.. code-block:: shell

    python -m scripts.token --key h8Ewzt2CUeAhn9sHHK5EtMn7pz4nA
    Admin Token: ad8428a05f63d948
    export atok=ad8428a05f63d948
    abaco run -V -m '{"name": "index", "uuid":"1079f67e-0ef6-52fe-b4e9-d77875573860","filters":[{"level":"1","patterns":[".bam$",".sam$"]}]}' -q token=$atok jobs-indexer.prod


Manually Marking a Job as Indexed
---------------------------------

The jobs-indexer will automatically send an **indexed** event to the target
job when indexing completes. Sometimes, though, a job might end up stuck in
the ``INDEXING`` state. To manually advance it, send it an **indexed** event.

.. code-block:: shell

    python -m scripts.token --key h8Ewzt2CUeAhn9sHHK5EtMn7pz4nA
    Admin Token: ad8428a05f63d948
    export atok=ad8428a05f63d948
    abaco run -V -m '{"name": "indexed", "uuid":"1079f67e-0ef6-52fe-b4e9-d77875573860"}' -q token=$atok jobs-indexer.prod

Authentication
--------------

Direct POSTs to a **PipelineJobs Indexer** must be authenticated. One usually
sends a valid TACC.cloud Oauth2 Bearer token with the request (this is the
default expectation for ``curl`` and ``abaco cli``, but this assumes your
account has been granted **EXECUTE** rights on the Reactor. For shared
infrastructure and services, one will instead send a special string known as a
a **nonce** along with the HTTP request.

JSON Schemas
------------

These are the reference documents used to validate messages received by the
Jobs Indexer reactor.

.. literalinclude:: schemas/index.jsonschema
   :language: json
   :linenos:
   :caption: pipelinejob_index

.. literalinclude:: schemas/indexed.jsonschema
   :language: json
   :linenos:
   :caption: pipelinejob_indexed
