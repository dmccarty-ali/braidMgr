# =============================================================================
# Demo Feature
# A narrated walkthrough of braidMgr for recording
# =============================================================================

@demo
Feature: braidMgr Demo Walkthrough
  A narrated demonstration of braidMgr's key features

  Scenario: Complete Application Demo
    # --- Introduction ---
    Given I show the narration "Welcome to braidMgr" with description "A multi-tenant RAID log management application for project teams"
    And I wait for "3" seconds

    # --- Login Flow ---
    Given I am on the "login" page
    And I show the narration "Secure Authentication" with description "Users sign in with email and password. OAuth support for Google and Microsoft coming soon."
    And I wait for "3" seconds

    When I fill in "Email" with "e2e-test@example.com"
    And I fill in "Password" with "E2eTestPass123"
    And I show the narration "Entering Credentials" with description "Form validation ensures proper input before submission"
    And I wait for "2" seconds

    When I click the "Sign in" button
    And I wait for "2" seconds

    # --- Project Selection ---
    Then I show the narration "Project Selection" with description "Users see all projects they have access to. Multi-tenant architecture keeps data isolated."
    And I wait for "3" seconds

    When I click on project "Website Modernization"
    And I wait for "2" seconds

    # --- Dashboard ---
    Then I show the narration "Project Dashboard" with description "At-a-glance summary of project health with RAID item counts and attention alerts"
    And I wait for "4" seconds

    And I show the narration "Summary Cards" with description "Quick counts for Risks, Actions, Issues, Decisions, Deliverables, Plan Items, and Budget items"
    And I wait for "3" seconds

    And I show the narration "Workstreams" with description "Items are organized into workstreams for better tracking and filtering"
    And I wait for "3" seconds

    # --- All Items View ---
    When I click the "All Items" link
    And I wait for "2" seconds
    Then I show the narration "All Items View" with description "Complete list of all RAID items with sorting, filtering, and search capabilities"
    And I wait for "4" seconds

    # --- Active Items View ---
    When I click the "Active Items" link
    And I wait for "2" seconds
    Then I show the narration "Active Items View" with description "Items grouped by severity indicator - focus on what needs attention first"
    And I wait for "4" seconds

    # --- Timeline View ---
    When I click the "Timeline" link
    And I wait for "2" seconds
    Then I show the narration "Timeline View" with description "Gantt-style visualization showing item schedules and dependencies"
    And I wait for "4" seconds

    # --- Chronology View ---
    When I click the "Chronology" link
    And I wait for "2" seconds
    Then I show the narration "Chronology View" with description "Items organized by month for historical tracking and reporting"
    And I wait for "4" seconds

    # --- Help View ---
    When I click the "Help" link
    And I wait for "2" seconds
    Then I show the narration "Help & Documentation" with description "Quick reference guides and documentation available in-app"
    And I wait for "3" seconds

    # --- Conclusion ---
    When I click the "Dashboard" link
    And I wait for "2" seconds
    Then I show the narration "Thank You" with description "braidMgr - Streamlined RAID log management for modern teams"
    And I wait for "4" seconds
