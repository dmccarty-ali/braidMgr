# =============================================================================
# Items Feature
# Tests item viewing and filtering on the All Items page
# =============================================================================

Feature: Item Management
  As a project manager
  I want to view and filter project items
  So that I can track my RAID log effectively

  Background:
    Given I am logged in
    And I am on the "items" page

  # ===========================================================================
  # Viewing Items
  # ===========================================================================

  Scenario: Items page displays item table
    Then I should see the "All Items" heading
    And I should see a table with items

  Scenario: Items table shows item details
    Then I should see item numbers in the table
    And I should see item types in the table
    And I should see item titles in the table

  # ===========================================================================
  # Filtering Items
  # ===========================================================================

  Scenario: User can filter items by type
    When I select "Risk" from the type filter
    Then all visible items should be of type "Risk"

  Scenario: User can filter items by indicator
    When I select "In Progress" from the indicator filter
    Then all visible items should have indicator "In Progress"

  Scenario: User can search items by title
    When I search for "migration"
    Then visible items should contain "migration" in the title

  Scenario: User can clear filters
    Given I have applied filters
    When I click the "Clear Filters" button
    Then all filters should be cleared
    And I should see all items
