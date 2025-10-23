Feature: Parameter definitions and validation
  In order to ensure parameters behave correctly
  As a configuration system
  I want parameter definitions to include required fields and obey persistence, type, alias and runtime-only rules

  Scenario: Parameter definition has required fields
    Given a parameter definition with name "username" and type "text"
    When the parameter definition is validated
    Then validation succeeds

  Scenario: Missing required field causes validation failure
    Given a parameter definition missing the "name" field
    When the parameter definition is validated
    Then validation fails with "missing name"

  Scenario: Parameter alias resolution
    Given a parameter definition with name "config-infile" and alias "--save-config"
    When a user provides "--save-config" on the CLI
    Then the parameter "config-infile" is bound with the provided value

  Scenario: Persistence flags respected during save/load
    Given a parameter "temp-token" marked as runtime-only
    When configuration is saved to disk
    Then "temp-token" is not persisted

  Scenario: Default values applied when not provided
    Given a parameter "retries" with type "number" and default value "3"
    When a command is prepared without "retries"
    Then "retries" is set to 3

  Scenario: Type validation enforces types
    Given a parameter "timeout" with type "number"
    When a user sets "timeout" to "fast"
    Then validation fails with "invalid type for timeout"
