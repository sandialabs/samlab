Feature: Observations
    Scenario: Ingesting observations
        Given a database named observations-1
        And a sample observation generator
        When the generator is used for ingestion
        Then there will be a collection named observations
        And the collection length will be 3
        And each document attributes field will equal {"c": "d"}
        And each document will contain a content field
        #And each document content-type field will equal "text/plain"
        And each document will contain a created field
        And each document tags field will equal ["a", "b"]
        And each content field will contain an "array" role with content-type "application/x-numpy-array"
        And each content field will contain a "string" role with content-type "text/plain; charset=utf-8"

    Scenario Outline: Ingest an observation
        Given a database named test
