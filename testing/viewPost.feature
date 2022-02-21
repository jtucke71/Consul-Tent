Jake -
Scenario: As a user, I want to be able to able to view the questions and posts of other users.
     Given: I am signed in to my account
     And: I am on the "Home" page
     When: I click the "View Forums" button
     Then: I should be taken to the "Questions" page
     And: I should see a scrollable list of user posts
     And: I should see the "Up-Vote" button beside each post
     And: I should see the "Down-Vote" button below the "Up-vote" button
