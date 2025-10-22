Feature: Configuration parameters and command sequencing
  In order to understand and verify the system configuration model and command ordering
  As a developer or tester
  I want readable scenarios that describe parameters, persistence, runtime-only behaviour, commands and phase sequencing

  Background:
    Given parameter definitions include keys: "name", "description", "bind_to", "type", "aliases", "required", "persistence", "switch-list", "default-value", and "runtime-only"
    And parameter types include: "text", "number", "toggle", and "list"
    And persistence options include: "always" and "never"
    And commands expose metadata keys: "command-name", "required-params", "description", "function", "sequence-before", "sequence-after", "require-before", "next-commands", "trigger-param", and "command-phase"
    And phases are ordered: "phase-setup", "phase-cleanup", "phase-execution", "phase-teardown", "phase-end"

  Scenario: Parameters declare required fields and optional metadata
    Given a parameter is declared
    Then it must include "name" and "type"
    And it may include description, aliases, required, persistence, switch-list, default-value, and runtime-only

  Scenario: Parameter types are validated
    Given a parameter declares a type
    Then the type is one of the allowed types ("text","number","toggle","list")

  Scenario: Persistence rules and runtime-only semantics
    Given a parameter declares persistence
    When persistence is validated
    Then persistence must be "always" or "never"
    And a parameter marked "runtime-only" is treated as non-persistent (not stored between runs)

  Scenario: Runtime-only parameters validated at runtime
    Given a runtime-only parameter is required by a command
    When the queue is validated before execution
    Then the runtime-only parameter is NOT required at queue-start
    And when the command runs, the runtime-only parameter must be present or the command fails

  Scenario: Commands enforce required parameters
    Given a command declares "required-params"
    When invoking the command
    Then all required bind names must exist in the current configuration or an error is raised

  Scenario: Sequence-before and sequence-after determine relative ordering
    Given command B lists A in its sequence-before (or A listed in B's sequence-after)
    When a queue is built for the same phase
    Then A must be scheduled before B

  Scenario: require-before enqueues prerequisites automatically
    Given command X lists commands in "require-before"
    When X is queued
    Then each require-before command is enqueued and executed before X

  Scenario: next-commands are enqueued after completion
    Given a command lists "next-commands"
    When that command completes successfully
    Then listed next-commands are added to the queue (after the current)

  Scenario: trigger-param maps parameter changes to commands
    Given a command maps a parameter name via "trigger-param"
    When that parameter is set prior to execution
    Then the mapped command is enqueued (unless its phase already ran)

  Scenario: Phase ordering is respected
    Given commands assigned to phases
    When the system executes phases
    Then phases run in the order: phase-setup, phase-cleanup, phase-execution, phase-teardown, phase-end

  Scenario: Default phase assignment for commands
    Given a command with no "command-phase"
    When the command is queued
    Then it is assigned the default phase "phase-execution"
