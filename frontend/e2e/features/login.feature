# =============================================================================
# Login Feature
# Tests user authentication flows
# =============================================================================
# This feature file describes login behavior in plain English.
# Each Scenario is an independent test case.
# Given/When/Then steps map to step definitions in e2e/steps/
# =============================================================================

Feature: User Login
  As a user of braidMgr
  I want to log in to my account
  So that I can access my projects and data

  Background:
    # This runs before each scenario in this feature
    Given I am not logged in

  # ===========================================================================
  # Happy Path Scenarios
  # ===========================================================================

  Scenario: Successful login with valid credentials
    Given I am on the "login" page
    When I log in with valid credentials
    Then I should be redirected to the dashboard
    And I should be logged in

  Scenario: User can navigate to registration page
    Given I am on the "login" page
    When I click the "Sign up" button
    Then I should see the "Create account" heading

  # ===========================================================================
  # Error Scenarios
  # ===========================================================================

  Scenario: Login fails with invalid credentials
    Given I am on the "login" page
    When I log in with invalid credentials
    Then I should see an authentication error
    And the URL should contain "login"

  # Note: Empty field validation uses HTML5 native browser validation (required attribute)
  # which shows browser tooltips rather than testable DOM text

  # ===========================================================================
  # Security Scenarios
  # ===========================================================================

  Scenario: Unauthenticated user is redirected to login
    Given I am not logged in
    When I navigate to "/projects"
    Then I should be redirected to the login page
