var graphData, newData, objData, objOData, objStore, processDropFetch, processTreeFetch, updateSelects,
  __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

dojo.require("dojo.io.script");

dojo.require("dojo.store.Memory");

dojo.require("dojo.parser");

dojo.require("dojo.data.ObjectStore");

dojo.require("dijit.Tree");

dojo.require("dojo.store.Observable");

dojo.require("dijit.form.Select");

dojo.require("dijit.form.FilteringSelect");

dojo.require("dijit.form.DateTextBox");

dojo.require("dojox.form.CheckedMultiSelect");

newData = [];

Sort(out(the(Dropdowns)));

dojo.xhrGet({
  url: "jsonnav",
  handleAs: "json",
  sync: true,
  load: function(jsonData) {
    console.log("IO COMPLETE");
    newData = jsonData;
    return console.log(jsonData);
  }
});

objData = new dojo.store.Memory({
  data: newData.list
});

objData.getRoot = function(onItem, onError) {
  var root;
  console.log("Get Root Called");
  root = this.get("root");
  return onItem(root);
};

objData.getChildren = function(object, onComplete, onError) {
  var children;
  children = this.query({
    parent: object.id
  });
  return onComplete(children);
};

objData.mayHaveChildren = function(object) {
  var children;
  children = __indexOf.call(object, "children") >= 0;
  return object.children;
};

objData.getLabel = function(object) {
  return object.name;
};

objData.filterTemp = function(object) {
  if (!object.sensorTypeId) return true;
  return object.sensorTypeId === 0;
};

objOData = new dojo.store.Observable(objData);

objStore = new dojo.data.ObjectStore({
  objectStore: objOData
});

dojo.addOnLoad(function() {
  var tree;
  tree = new dijit.Tree({
    model: objOData,
    showRoot: false
  }, 'treeNode');
  return tree.startup();
});

dojo.addOnLoad(function() {
  var dropClear, dropFetch, sensorType, startDateTree, stopDateTree, treeFetch;
  sensorType = new dijit.form.FilteringSelect({
    name: "sensorType",
    store: objStore,
    placeHolder: "(Optional) Sensor Type",
    query: {
      "type": "sensorType"
    }
  }, "sensorType");
  sensorType.startup();
  dropFetch = new dijit.form.Button({
    showLabel: true,
    label: "Get Data",
    onClick: function() {
      console.log("Drop Button Pressed");
      return processDropFetch();
    }
  }, "dropFetch");
  dropFetch.startup();
  startDateTree = new dijit.form.DateTextBox({
    name: "startDateTree"
  }, "startDateTree");
  stopDateTree = new dijit.form.DateTextBox({
    name: "stopDateTree"
  }, "stopDateTree");
  treeFetch = new dijit.form.Button({
    showLabel: true,
    label: "Get Tree Data",
    onClick: function() {
      console.log("Tree Button Pressed");
      return processTreeFetch();
    }
  }, "treeFetch");
  treeFetch.startup();
  return dropClear = new dijit.form.Button({
    showLabel: true,
    label: "reset",
    onClick: function() {
      dijit.byId("startDateTree").reset();
      dijit.byId("stopDateTree").reset();
      return dijit.byId("sensorType").reset();
    }
  }, "dropClear");
});

updateSelects = function() {
  var houseSelect, houseValue, nodeSelect, nodeValue, sensorSelect, sensorValue;
  console.log("Update Selects");
  houseSelect = dijit.byId("houseSelect");
  nodeSelect = dijit.byId("nodeSelect");
  sensorSelect = dijit.byId("sensorSelect");
  console.log("House Displayed " + houseSelect.displayedValue + " Value " + houseSelect.value);
  console.log("Node Displayed " + nodeSelect.displayedValue + " Value " + nodeSelect.value);
  console.log("Sensor Displayed " + sensorSelect.displayedValue + " Value " + sensorSelect.value);
  houseValue = houseSelect.value;
  nodeValue = nodeSelect.value;
  sensorValue = sensorSelect.value;
  if (houseValue === -1) houseValue = "*";
  if (nodeValue === -2) nodeValue = "*";
  if (sensorValue === -3) sensorValue = "*";
  nodeSelect.query = {
    type: "node",
    parent: houseValue
  };
  return sensorSelect.query = {
    type: "sensor",
    parent: nodeValue
  };
};

processDropFetch = function() {
  var houseSelect, nodeSelect, sensorSelect, startDate, startTime, stopDate, stopTime;
  houseSelect = dijit.byId("houseSelect");
  nodeSelect = dijit.byId("nodeSelect");
  sensorSelect = dijit.byId("sensorSelect");
  console.log("House Displayed " + houseSelect.displayedValue + " Value " + houseSelect.value);
  console.log("Node Displayed " + nodeSelect.displayedValue + " Value " + nodeSelect.value);
  console.log("Sensor Displayed " + sensorSelect.displayedValue + " Value " + sensorSelect.value);
  startDate = dijit.byId("startDateTree").value;
  stopDate = dijit.byId("stopDateTree").value;
  console.log(startDate);
  if (startDate) startTime = startDate.getTime() / 1000.0;
  if (stopDate) stopTime = stopDate.getTime() / 1000.0;
  console.log("Fetching Data");
  dojo.io.script.get({
    url: "http://127.0.0.1:6543/jsonFetch",
    content: {
      type: "drop",
      houseId: houseSelect.value,
      nodeId: nodeSelect.value,
      sensorId: sensorSelect.value,
      startTime: startTime,
      stopTime: stopTime
    },
    callbackParamName: "callback",
    load: function(jsonData) {
      return graphData(jsonData);
    }
  });
  return console.log("Done");
};

processTreeFetch = function() {
  var item, sensorType, sensorTypeValue, startDate, startTime, stopDate, stopTime, tempItem, theTree, treeItems, treeList, _i, _len;
  theTree = dijit.byId("treeNode");
  treeItems = theTree.selectedItems;
  startDate = dijit.byId("startDateTree");
  stopDate = dijit.byId("stopDateTree");
  if (startDate.value) startTime = startDate.value.getTime() / 1000;
  if (stopDate.value) stopTime = stopDate.value.getTime() / 1000;
  sensorTypeValue = -1;
  sensorType = dijit.byId("sensorType");
  if (sensorType.displayedValue === "Temperature") {
    sensorTypeValue = 0;
  } else {
    sensorTypeValue = sensorType.value;
  }
  console.log("Sensor Type ");
  console.log(sensorTypeValue);
  console.log("-----");
  treeList = [];
  console.log("---- Tree Loop----");
  for (_i = 0, _len = treeItems.length; _i < _len; _i++) {
    item = treeItems[_i];
    console.log(item);
    if (item.type === "deployment") {
      console.log("Deployment Selected");
      tempItem = {
        deploymentId: item.id
      };
    }
    if (item.type === "house") {
      console.log("House Selected");
      tempItem = {
        deploymentId: item.parent,
        houseId: item.id
      };
    }
    if (item.type === "location") {
      console.log("Location Selected");
      tempItem = {
        locationId: item.id
      };
    }
    if (item.type === "node") {
      console.log("Node Selected");
      tempItem = {
        nodeId: item.id,
        location: item.location
      };
    }
    if (item.type === "sensor") {
      console.log("Sensor Selected");
      tempItem = {
        sensorId: item.id,
        location: item.location
      };
    }
    treeList.push(tempItem);
    console.log(tempItem);
  }
  console.log("--- EOL ----");
  console.log(treeList);
  dojo.io.script.get({
    url: "http://127.0.0.1:6543/jsonFetch",
    content: {
      type: "tree",
      sensorType: sensorTypeValue,
      treeItems: dojo.toJson(treeList),
      startTime: startTime,
      stopTime: stopTime
    },
    callbackParamName: "callback",
    load: function(jsonData) {
      console.log("~~~~~~~~~~~");
      console.log(jsonData);
      console.log("~~~~~~~~~~~");
      return graphData(jsonData);
    }
  });
  return console.log("Done");
};

graphData = function(jsonData) {
  var chart, options;
  console.log("Graphing");
  console.log(jsonData);
  options = {
    chart: {
      renderTo: "theGraph",
      spacingBottom: 40
    },
    title: {
      text: "Time Series Data"
    },
    yAxis: {
      title: {
        text: "Default Y Title"
      }
    },
    legend: {
      enabled: true,
      verticalAlign: "bottom",
      y: 35
    },
    credits: {
      enabled: false
    },
    xAxis: {
      title: {
        text: "Time"
      }
    },
    series: [
      {
        name: "Series",
        data: [[1, 1], [2, 2]]
      }
    ]
  };
  options.title.text = jsonData.title;
  options.series = jsonData.series;
  options.yAxis.title.text = jsonData.yText;
  chart = Highcharts.StockChart(options);
  return console.log("Done");
};
