Feature: Streaming data
    Scenario: Windowed arrays
        Given a random array input with shape (100, 100, 3)
        And a single value stream generator
        And an array window generator with shape (10, 10) and stride (10, 10)
        When the stream generator is exhausted
        Then there will be 100 stream datums
        And each stream datum input will be an array
        And each stream datum input array will have shape (10, 10, 3)

    Scenario: Windowed arrays 2
        Given a random array input with shape (95, 95, 3)
        And a single value stream generator
        And an array window generator with shape (10, 10) and stride (10, 10)
        When the stream generator is exhausted
        Then there will be 100 stream datums
        And each stream datum input will be an array
        And each stream datum input array will have shape (10, 10, 3)
