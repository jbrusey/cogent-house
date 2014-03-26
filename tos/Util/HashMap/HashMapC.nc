// -*- c -*-

#define SPECIAL 0xffff

generic module HashMapC(uint16_t size) @safe()
{
  provides interface Map;
}

implementation
{
  uint16_t keys [size];
  uint16_t values [size];

  uint16_t hash(uint16_t x) {
    return x;
  }

  command void Map.init() { 
    int i;
    for (i = 0; i < size; i++) 
      keys[i] = SPECIAL;
  }

  /** find either the index of the first matching entry for the key OR
      the correct location for inserting the key */
  int lookup(uint16_t key) {
    int h, h1;
    h = h1 = hash(key) % size;
    while (key != keys[h] && keys[h] != SPECIAL) {
      h = (h + 1) % size; // linear probing
      if (h == h1) 
	return -1; // not found
    }
    return h;
  }

  command int Map.put(uint16_t key, uint16_t value)
  {
    int h;
    h = lookup(key);
    if (h == -1) 
      return FALSE;
    keys[h] = key;
    values[h] = value;
    return TRUE;
  }
    
  command int Map.get(uint16_t key, uint16_t *pvalue)
  {
    int h;
    h = lookup(key);
    if (keys[h] == key) {
      *pvalue = values[h];
      return TRUE;
    }
    else 
      return FALSE;
  }

  command int Map.contains(uint16_t key)
  {
    int h;
    h = lookup(key);
    if (keys[h] == key) {
      return TRUE;
    }
    else 
      return FALSE;
  }    
}
  
