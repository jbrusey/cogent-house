/* -*- c -*- */

interface Map
{
	/**
	* init empties out the map and should be called before using
	* it
	*/
	command void init();

	/**
	* put either inserts a new entry mapping key to value or
	* overwrites an existing entry.  Returns TRUE if successful or
	* FALSE if the table is full.
	*/
	command int put(uint16_t key, uint16_t value);

	/**
	* get returns the value corresponding to key.
	* returns TRUE if found, or FALSE if not. 
	*/
	command int get(uint16_t key, uint16_t *pvalue);

	/**
	* contains returns TRUE if key is in the map
	*/
	command int contains(uint16_t key);


}

