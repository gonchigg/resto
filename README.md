# resto project

Program to handle a waiting queue on a resto/bar and inform to the waiters the waiting time.

  * The resto/bar has multiple Tables. Each Table has:
    * Multiple capacities.
    * A Histogram that defines the probability function of when the group of clients is going to leave.
    * Possibility of being joined with onother Table to form a new Table
    
  * The Clients Queue has multiple Clients who arrive with a defined probability function.
  
  The Program calculates the probability of the clients in the queue of being let in in function of the time. The algorithm eats:
  * The state of all the Tables in the bar
  * The state of the Queue
  * The histogram of all tables
  * The probability of the Queue of being altered
