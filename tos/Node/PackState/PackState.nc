#include "packstate.h" 
interface PackState
{
	/**
	* 
	*/
	command void clear();

	/**
	* 
	*/
	command int add(int key, float value);


	/**
	* 
	*/
	command int pack(packed_state_t *ps);


	/**
	* 
	*/
	command void unpack(packed_state_t *ps);


	/**
	* 
	*/
	command float get(int i);


	/**
	* 
	*/
	command int haskey(int i);


}

