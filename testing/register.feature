Penuel -
Scenario: As a user, I need a way to register for a new user account
     Given: I am on the "Home" page
     When: I click the "Register" button
     Then: I should be taken to the "Create Account" page
     And: I should see the "First name" text entry field
     And: I should see the "Last name" text entry field
     And: I should see the "Email" text entry field
     And: I should see the "Username" text entry field
     And: I should see the "Password" text entry field
     And: I should see the "Confirm" text entry field
     When: I click on the "First Name" text entry field
     Then: I should be able to enter my first name
     When: I click on the "Last Name" text entry field
     Then: I should be able to enter my last name
     When: I click on the "Email" text entry field
     Then: I should be able to enter an email address
     When: I click on the "Username" text entry field
     Then: I should be able to enter a username
     When: I click on the "Password" text entry field
     Then: I should be able to enter a password
     When: I click on the "Confirm" text entry field
     Then: I should be able to re-enter my chosen password
     When: I click the "Create Account" button
     Then: I should be returned to the Home screen
