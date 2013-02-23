/* -*- c -*- */
/*************************************************************
 *
 * ParserC.nc
 *
 * simplified xml parser for dealing with current cost
 *
 * @author James Brusey
 * @date 2011-05-17
 *
 * history:
 * 1. conversion to C
 * 2. conversion to nesc, may 2011
 *
 *************************************************************/

#ifdef DEBUG 
#  include "printf.h"
#endif
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#define MAX_VALUE_LENGTH 20
#define MAX_PATH_LENGTH 100
#define MAX_NAME_LENGTH 20

module ParserC { 
  provides interface Parser;
  uses interface BigAsyncQueue<uint8_t> as MsgQueue;
}

implementation { 
  uint8_t cc = ' ', pb = FALSE, lc = ' ', nc = ' ';
  char errstr[200];




  /** nextc returns the current char and also calls for the next
   *  one allowing a one character look-ahead
   */
  uint8_t nextc() {
    if (pb) {
      pb = FALSE;
      lc = cc;
      cc = nc;
    }
    else {
      lc = cc;
      if (call MsgQueue.empty())
	cc = 0;
      else 
	cc = call MsgQueue.dequeue();
    
    }
    return lc;
  }

  /** pushback pushes the last character back. There is only room for a
   *  single character to be pushed back.
   */
  void pushback() {
    nc = cc;
    cc = lc;
    pb = TRUE;
  }

  void allowwhitespace() {
    while (cc == ' ' || cc == '\n' || cc == '\t' || cc == '\r')
      nextc();
  }

  error_t expect(int c) {
    allowwhitespace();
    if (cc != c) {
      sprintf(errstr, "expected %c received %c", c, cc);
      return FAIL;
    }
    nextc();
    return SUCCESS;
  }

  error_t pname(char *n, int len){
    /*
      name ::= alpha { alphanum }
    */
    int i;
    allowwhitespace();
    strncpy(n, "", len);
    n[0] = nextc();
    if (! isalpha(n[0])) {
      sprintf(errstr, "name must start with an alpha");
      return FAIL;
    }
    i = 1;
    while (isalnum(cc)) {
      if (i >= len - 1) {
	sprintf(errstr, "name too long");
	return FAIL;
      }
      n[i++] = nextc();
    }
    return SUCCESS;
  }

  error_t term(char *path);
  error_t pvalue(char *value, int len);
        
  error_t contents(char *path){
    /*
      contents ::= term {term} | value
    */
    char new_path[MAX_PATH_LENGTH];
    char value[MAX_VALUE_LENGTH];
    allowwhitespace();
    if (nextc() == '<') {
      /* lookahead one char */
      while (cc != '/') {
	/* if it is not an end token then it must be a new term */
	/* but we have to pushback the last char so that term */
	/* can use it. */
	pushback();
	if (strlen(path) + 2 > sizeof new_path) {
	  sprintf(errstr, "path name too long");
	  return FAIL; /* path would have been truncated */
	}
	strncpy(new_path, path, sizeof new_path);
	strncat(new_path, "/", sizeof new_path);
	if (term(new_path) != SUCCESS)
	  return FAIL;
	if (expect('<') != SUCCESS)
	  return FAIL;
      }
      pushback();
      return SUCCESS;
    }
    else {
      pushback();
      if (pvalue(value, sizeof value) != SUCCESS)
	return FAIL;
      signal Parser.onValue(path, value);
      return SUCCESS;
    }
  }

  error_t pvalue(char *value, int len) {
    /*
      value ::= [^<]*
    */
    int i = 0;
    strncpy(value, "", len);
    while (cc != '<') {
      if (i >= len - 1) {
	sprintf(errstr, "value too long");
	return FAIL;
      }
      value[i++] = nextc();
    }
    return SUCCESS;
  }

  error_t term(char *path){
    /* 
       term ::= '<' name '>' contents '<' '/' name '>'
    */
    char name[MAX_NAME_LENGTH];
    char n1[MAX_NAME_LENGTH];
    char new_path[MAX_PATH_LENGTH];
    if (! (expect('<') == SUCCESS &&
	   pname(name, sizeof name) == SUCCESS &&
	   expect('>') == SUCCESS))
      return FAIL;
    if (strlen(path) + strlen(name) + 1 > sizeof new_path) {
      sprintf(errstr, "path name too long");
      return FAIL; /* path would have been truncated */
    }
    strncpy(new_path, path, sizeof new_path);
    strncat(new_path, name, sizeof new_path);
    if (! (contents(new_path) == SUCCESS &&
	   expect('<') == SUCCESS && 
	   expect('/') == SUCCESS &&
	   pname(n1, sizeof n1) == SUCCESS)) 
      return FAIL;
    if (strcmp(name, n1) != 0) {
      sprintf(errstr, "end name mismatch, %s != %s", name, n1);
      return FAIL;
    }
    return expect('>');

  }

  command error_t Parser.parse() {
    error_t result;
    if (cc == 0) 
      nextc();
#ifdef DEBUG
    printf("cc is currently %d\n", cc);
    printfflush();
#endif 
    strncpy(errstr, "no error recorded", sizeof errstr);
    result = term("/");
    if (result == FAIL) { 
      // skip until byte queue is empty or cr or nl
      do { 
	nextc();
      } while (cc != 0 && cc != '\n' && cc != '\r' && cc != 0xED);
      /* ascii 237 (0xed) is used to terminate history display */
    }
    return result;
  }

  command char *Parser.lastError() { 
    return errstr;
  }
}
