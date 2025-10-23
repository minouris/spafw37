Feature: Command definitions and queueing behavior
  In order to orchestrate work
  As a command-queue system
  I want commands to declare requirements and sequencing so queues run predictably

  Scenario: Command requires parameters before execution
    Given a command "deploy" that requires params "image" and "tag"
    When the command "deploy" is queued without "tag"
    Then the queue rejects the command with "missing required param: tag"

  Scenario: Commands can be sequenced before/after another by user
    Given command "build" with sequence-before "test"
    When a user queues "test"
    Then "build" is queued to run before "test"

  Scenario: Commands automatically require other commands
    Given command "migrate" requires-before "backup"
    When the user queues "migrate"
    Then "backup" is automatically queued and precedes "migrate"

  Scenario: Commands can enqueue next-commands after successful run
    Given command "install" lists next-commands "configure"
    When "install" completes successfully
    Then "configure" is automatically queued in the appropriate phase

  Scenario: Command triggered by parameter change
    Given command "reload" has trigger-param "config-infile"
    When "config-infile" is set or changed at runtime
    Then "reload" is queued for execution in the current or next allowed phase

  Scenario: Command phase assignment defaults to execution
    Given a command "run-task" without a phase
    When it is queued
    Then it is assigned the default phase "phase-execution"
