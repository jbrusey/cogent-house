
require(["dojo/topic"], function(topic) {
  console.log("Topic Fired");
  return topic.subscribe("navTree", function(arg1) {
    return console.log("--- FIRED --- ", arg1);
  });
});
