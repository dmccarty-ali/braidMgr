# =============================================================================
# Registration Feature
# Tests user registration flows including auto-organization creation
# =============================================================================
# This feature verifies that new users can register and immediately access
# the projects page without errors. Regression test for the "Failed to load
# projects" bug where new users had no organization context.
# =============================================================================

Feature: User Registration
  As a new user of braidMgr
  I want to create an account
  So that I can start managing my projects

  Background:
    Given I am not logged in

  # ===========================================================================
  # Happy Path - Critical Regression Test
  # ===========================================================================

  Scenario: New user can register and access projects page
    Given I am on the "register" page
    When I register with a unique email and valid password
    Then I should be redirected to the projects page
    And I should not see "Failed to load projects"
    And I should see "Select a Project"
