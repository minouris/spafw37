Feature: Phase ordering and constraints for command queues
  In order to maintain a predictable lifecycle
  As a queue runner
  I want commands to be constrained by phase order and to allow adding commands to later phases only

  Background:
    Given the phase order is:
      | phase-setup |
      | phase-cleanup |
      | phase-execution |
      | phase-teardown |
      | phase-end |

  Scenario: Phases run in defined order
    When the runner executes phases
    Then "phase-setup" runs before "phase-cleanup"
    And "phase-cleanup" runs before "phase-execution"

  Scenario: Cannot enqueue commands into a phase that already ran
    Given the runner has completed "phase-setup"
    When a command attempts to add a new command into "phase-setup"
    Then the addition is rejected with "cannot add to completed phase"

  Scenario: Commands may enqueue into later phases
    Given the runner is executing "phase-setup"
    When a command enqueues a follow-up command into "phase-execution"
    Then the follow-up command is accepted and will run when "phase-execution" starts

  Scenario: Triggered commands are not scheduled into already-completed phases
    Given a parameter-triggered command targets "phase-setup"
    And "phase-setup" has already completed
    When the parameter is set at runtime
    Then the system schedules the triggered command into the next appropriate phase or rejects with "phase passed"
