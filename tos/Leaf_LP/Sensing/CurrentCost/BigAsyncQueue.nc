
/**
 *  Interface to a queue that supports async. Based on BigQueue
 *
 *  @author James Brusey
 */

   
interface BigAsyncQueue<t> {

  /**
   * Returns if the queue is empty.
   *
   * @return Whether the queue is empty.
   */
  async command bool empty();

  /**
   * The number of elements currently in the queue.
   * Always less than or equal to maxSize().
   *
   * @return The number of elements in the queue.
   */
  async command uint16_t size();

  /**
   * The maximum number of elements the queue can hold.
   *
   * @return The maximum queue size.
   */
  async command uint16_t maxSize();

  /**
   * Get the head of the queue without removing it. If the queue
   * is empty, the return value is undefined.
   *
   * @return The head of the queue.
   */
  async command t head();
  
  /**
   * Remove the head of the queue. If the queue is empty, the return
   * value is undefined.
   *
   * @return The head of the queue.
   */
  async command t dequeue();

  /**
   * Enqueue an element to the tail of the queue.
   *
   * @param newVal - the element to enqueue
   * @return SUCCESS if the element was enqueued successfully, FAIL
   *                 if it was not enqueued.
   */
  async command error_t enqueue(t newVal);

}
