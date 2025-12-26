# =============================================================================
# Dashboard Feature
# Tests the main dashboard view and navigation
# =============================================================================

Feature: Project Dashboard
  As a logged-in user
  I want to see my project dashboard
  So that I can get an overview of my project status

  Background:
    Given I am logged in

  # ===========================================================================
  # Dashboard Overview
  # ===========================================================================

  Scenario: Dashboard displays project summary
    Given I am on the "dashboard" page
    Then I should see the "Dashboard" heading
    And I should see "Workstreams"

  Scenario: Dashboard shows attention section
    Given I am on the "dashboard" page
    Then I should see "Attention Needed"

  # ===========================================================================
  # Navigation from Dashboard
  # ===========================================================================

  Scenario: User can navigate to All Items from dashboard
    Given I am on the "dashboard" page
    When I click the "All Items" link
    Then I should see the "All Items" heading
    And the URL should contain "items"

  Scenario: User can navigate to Active Items from dashboard
    Given I am on the "dashboard" page
    When I click the "Active Items" link
    Then I should see the "Active Items" heading
    And the URL should contain "active"

  Scenario: User can navigate to Timeline from dashboard
    Given I am on the "dashboard" page
    When I click the "Timeline" link
    Then I should see the "Timeline" heading
    And the URL should contain "timeline"

  Scenario: User can navigate to Chronology from dashboard
    Given I am on the "dashboard" page
    When I click the "Chronology" link
    Then I should see the "Chronology" heading
    And the URL should contain "chronology"

  Scenario: User can navigate to Help from dashboard
    Given I am on the "dashboard" page
    When I click the "Help" link
    Then I should see the "Help" heading
    And the URL should contain "help"
