Feature: Timeseries

    Scenario Outline: Reservoir
        Given a reservoir object with size <size> and seed <seed>
        When the sequence <sequence> is added to the reservoir
        Then the reservoir length should match <length>
        And the reservoir should contain <result>

        Examples:
            | size | seed | sequence                       | length | result             |
            | 3    | 1234 | []                             | 0      | []                 |
            | 3    | 1234 | [1]                            | 1      | [1]                |
            | 3    | 1234 | [1, 2]                         | 2      | [1, 2]             |
            | 3    | 1234 | [1, 2, 3]                      | 3      | [1, 2, 3]          |
            | 3    | 1234 | [1, 2, 3, 4]                   | 3      | [1, 2, 3]          |
            | 3    | 1234 | [1, 2, 3, 4, 5]                | 3      | [1, 2, 3]          |
            | 3    | 1234 | numpy.arange(10)               | 3      | [0, 1, 2]          |
            | 3    | 1234 | numpy.arange(20)               | 3      | [0, 10, 2]         |
            | 5    | 1234 | numpy.arange(20)               | 5      | [0, 11, 2, 5, 8]   |
