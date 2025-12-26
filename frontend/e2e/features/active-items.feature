# =============================================================================
# Active Items Feature
# Tests the Active Items view with severity grouping
# =============================================================================

Feature: Active Items View
  As a project manager
  I want to see items grouped by severity
  So that I can focus on the most critical issues first

  Background:
    Given I am logged in
    And I am on the "active" page

  # ===========================================================================
  # Active Items Display
  # ===========================================================================

  Scenario: Active Items page shows severity groups
    Then I should see the "Active Items" heading
    And I should see severity group sections

  Scenario: Items are grouped by indicator severity
    Then critical items should appear before warning items
    And warning items should appear before normal items

  Scenario: Each severity group shows item count
    Then each severity group should show the number of items
