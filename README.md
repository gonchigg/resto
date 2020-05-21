# resto project

### Program to handle a waiting queue on a resto/bar and inform to the waiters the waiting time.

  * The resto/bar has multiple Tables. Each Table has:
    * Multiple capacities.
    * A Histogram that defines the probability function of when the group of clients is going to leave.
    * Possibility of being joined with onother Table to form a new Table
    
  * The Clients Queue has multiple Clients who arrive with a defined probability function.
  
  ### The Program calculates the probability of the clients in the queue of being let in in function of the time. The algorithm eats:
  * The state of all the Tables in the bar
  * The state of the Queue
  * The histogram of all tables
  * The probability of the Queue of being altered

### Usage

  * **calculate_probs.py** calculates the probability in function of the time.
    * **Simulation time:** defined inside the program
    * **Resto initial state:** defined in input_jsons/resto_vacio.json
    * **Queue initial state:** defined in input_jsons/cola_vacia.json
    * **Probability function of the tables:** defined in input_jsons/resto_vacio.json
    * **Probability function of the Queue:** defined inside *My.giveme_llegadas*

  * **calculate_statistics.py** calculates statistics of the program to see how it is going.

  * **Tree** inside it is defined the class *Tree* that it is used to calculate all the possibilities of arraging the clients in the tables

  * **My** inside are defined the classes Cola, Resto, Mesas, Clientes used to managing those.
