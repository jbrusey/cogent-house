
require(["dojo/store/Memory", "dojo/store/JsonRest", "dojo/data/ObjectStore", "dijit/Tree", "dojo/domReady!"], function(Memory, JsonRest, ObjectStore, Tree) {
  var dataStore, memStore, theTree, treeStore;
  console.log("Loading Data");
  memStore = new JsonRest({
    target: "jsonRest/"
  });
  console.log("Done");
  dataStore = new ObjectStore({
    objectStore: memStore
  });
  treeStore = new dijit.tree.TreeStoreModel({
    store: dataStore
  });
  theTree = new Tree({
    model: treeStore
  }, "treeNode");
  return theTree.startup();
});

require(["dijit/form/Button", "dijit/form/DateTextBox", "dijit/form/FilteringSelect", "dojo/data/ItemFileReadStore", "dojo/domReady!"], function(Button, DateTextBox, Select, ItemFileReadStore) {
  var clearData, getData, sensorType, showData, startDate, stopDate, typeStore;
  getData = new Button({
    label: "Get Data",
    onClick: function() {
      console.log("Getting Data");
      return showData();
    }
  }, "getData");
  getData.startup();
  clearData = new Button({
    label: "Clear",
    onClick: function() {
      dijit.byId("startDate").reset();
      dijit.byId("stopDate").reset();
      return dijit.byId("sensorType").reset();
    }
  }, "clearData");
  clearData.startup();
  startDate = new DateTextBox({
    name: "startDate"
  }, "startDate");
  startDate.startup();
  stopDate = new DateTextBox({
    name: "stopDate"
  }, "stopDate");
  stopDate.startup();
  typeStore = new ItemFileReadStore({
    url: "jsonnav"
  });
  sensorType = new Select({
    name: "sensorType",
    store: typeStore,
    query: {
      "type": "sensor"
    }
  }, "sensorType");
  sensorType.startup();
  return showData = function() {
    var content, outItems, theTree, treeItems, typeDisp, x;
    console.log("Show Data Called");
    theTree = dijit.byId("treeNode");
    treeItems = theTree.selectedItems;
    outItems = JSON.stringify((function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = treeItems.length; _i < _len; _i++) {
        x = treeItems[_i];
        _results.push(x.id);
      }
      return _results;
    })());
    console.log(outItems);
    startDate = dijit.byId("startDate").value;
    stopDate = dijit.byId("stopDate").value;
    sensorType = dijit.byId("sensorType").value;
    typeDisp = dijit.byId("sensorType").getDisplayedValue();
    console.log("Sensor Type >" + sensorType + "<");
    if (sensorType === "") {
      console.log(dijit.byId("sensorType"));
      if (dijit.byId("sensorType").getDisplayedValue() === "Temperature") {
        sensorType = 0;
      }
    }
    console.log(sensorType);
    content = {
      startDate: startDate,
      stopDate: stopDate,
      sensorType: sensorType,
      treeItems: outItems
    };
    console.log("Fetching Data");
    fetchData(content);
    return console.log("Graphs Done");
  };
}, console.log("Init Functions Called"));
