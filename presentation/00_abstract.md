# Project Overview

In this project, we're trying to understand how NBA teams play basketball in different ways. Instead of just looking at wins and losses, we're using machine learning to find natural patterns in how teams approach the game.

Think of it like sorting basketball teams into different "styles" - but instead of us deciding what those styles should be, we're letting the data tell us what patterns exist naturally. It's like if you had a huge pile of basketball cards and wanted to group similar players together, but instead of just grouping by position, you let all their stats determine how they get grouped.

We're using three main types of data:
1. Every shot taken in NBA games (where on the court, who took it, did it go in)
2. Every time a player got injured (what happened, how long they were out)
3. All the regular team stats (points, rebounds, etc.)

To find these patterns, we're using several machine learning techniques:
- K-means clustering: This helps us find distinct team "styles"
- Hierarchical clustering: This shows us how different styles relate to each other
- PCA: This helps us understand what aspects of the game matter most
- t-SNE: This helps us visualize how teams are similar or different
- Isolation Forest: This helps us find really unique or special team performances

What makes this approach special is that we're not starting with any assumptions about what makes teams different. Instead of saying "these are offensive teams and these are defensive teams", we're letting the data show us what kinds of teams naturally exist.

Through this analysis, we're hoping to:
- Discover what distinct styles of basketball exist in the NBA
- See how these styles have changed over time
- Understand what makes some teams revolutionary or unique
- Learn how injuries affect how teams play
- Find patterns in what makes teams successful

This is different from traditional analysis because instead of testing specific theories about basketball, we're letting the patterns emerge from the data itself. It's like having a conversation with the data and letting it tell us what's interesting, rather than just asking it to confirm what we already think we know.
