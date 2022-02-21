Jacob -
Scenario: As a user, I need a way to edit a post I made previously
     Given: I am on the "List of Posts" page
     When: I click the three vertical dots at the top-right of my previous post
     Then: I should see a menu pop up with options, "Edit", "Pin" and "Delete"
     When: I click the "Edit" button, my previous post will be editable
     Then: I should be able to replace my previous post with the newly edited one
     And: I will be returned to the "List of Posts"
