
/**
 *  A large asynchronous FIFO queue for passing data items between an
 *  async event and a subsequently posted task.
 *
 *  @author James Brusey
 */

   
generic module BigAsyncQueueC(typedef queue_t, uint16_t QUEUE_SIZE) {
  provides interface BigAsyncQueue<queue_t> as Queue;
}

implementation {

  queue_t queue[QUEUE_SIZE];
  uint16_t head = 0;
  uint16_t tail = 0;
  uint16_t size = 0;
  
  async command bool Queue.empty() {
    atomic {
      return size == 0;
    }
  }

  async command uint16_t Queue.size() {
    atomic { 
      return size;
    }
  }

  async command uint16_t Queue.maxSize() {
    return QUEUE_SIZE;
  }

  async command queue_t Queue.head() {
    atomic {
      return queue[head];
    }
  }

  async command queue_t Queue.dequeue() {
    queue_t t;
    atomic { 
      t = call Queue.head();
      if (!call Queue.empty()) {
	head++;
	head %= QUEUE_SIZE;
	size--;
      }
    }
    return t;
  }

  async command error_t Queue.enqueue(queue_t newVal) {
    error_t ok = FAIL;
    atomic { 
      if (call Queue.size() < call Queue.maxSize()) {
	queue[tail] = newVal;
	tail++;
	tail %= QUEUE_SIZE;
	size++;
	ok = SUCCESS;
      }
    }
    return ok;
  }
  
}
