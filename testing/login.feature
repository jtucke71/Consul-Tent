Noah -
Scenario: As a user, I want to be able to login to my account using my credentials.
    Given: I am on the "Home" page
    When: I click on the "Login" button
    Then: I should be taken to "Login" page
    And: I should see the "Username" text entry box
    And: I should see the "Password" text entry box
    When: I click on the "Username" text entry box
    Then: I should be able to enter my username
    When: I click on the "Password" text entry box
    Then: I should be able to enter my account password
    When: I click the "Sign In" button
    Then: I should see a "Welcome" message letting me know that I signed in
    And: I should be returned to the home screen
