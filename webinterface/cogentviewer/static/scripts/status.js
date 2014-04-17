var dateFormatter, getDateValue, setNodeId;

require(["dojo/date/stamp", "dojo/date/locale", "dijit/form/SimpleTextarea", "dijit/form/DateTextBox", "dijit/form/TextBox"]);

dateFormatter = function(dateStr) {
  var theDate;
  if (dateStr) {
    theDate = dojo.date.stamp.fromISOString(dateStr);
    return dojo.date.locale.format(theDate, {
      format: "short"
    });
  } else {
    return null;
  }
};

getDateValue = function() {
  return dojo.date.stamp.toISOString(this.widget.get('value'));
};

require(["dojo/store/JsonRest", "dojox/grid/DataGrid", "dojo/data/ObjectStore", "dojo/store/Cache", "dojo/store/Observable", "dojo/store/Memory", "dijit/form/Button", "dijit/form/FilteringSelect", "dijit/Dialog", "dojox/grid/cells/dijit", "dojo/domReady!"], function(jsonRest, dataGrid, ObjectStore, Cache, Observable, Memory, Button, FilteringSelect) {
  var addDeployment, addHouse, clearDeployment, clearHouse, clearSelectDep, clearSelectHouse, deleteDep, deleteHouse, depAddBtn, depClearBtn, depDelete, depHouseAddBtn, depHouseClearBtn, deployDataStore, deployFormatter, deployGrid, deployStore, houseButton, houseDataStore, houseDelete, houseDep, houseGrid, houseStore, newDep, newHouse, resetButton, saveDep;
  deployStore = Cache(Observable(jsonRest({
    target: "rest/deployment/"
  })), Memory());
  deployGrid = new dataGrid({
    store: deployDataStore = ObjectStore({
      objectStore: deployStore
    }),
    structure: [
      {
        name: "id",
        field: "id",
        width: "50px"
      }, {
        name: "name",
        field: "name",
        width: "100px",
        editable: true
      }, {
        name: "description",
        field: "description",
        width: "100px",
        editable: true
      }, {
        name: "startDate",
        field: "startDate",
        width: "150px",
        formatter: dateFormatter,
        editable: true,
        type: dojox.grid.cells.DateTextBox,
        getValue: getDateValue
      }, {
        name: "endDate",
        field: "endDate",
        width: "150px",
        formatter: dateFormatter,
        editable: true,
        type: dojox.grid.cells.DateTextBox,
        getValue: getDateValue
      }, {
        name: "table",
        field: "table",
        widht: "100px"
      }
    ]
  }, "deployGrid");
  deployGrid.startup();
  dojo.connect(deployGrid, 'onStyleRow', deployGrid, function(row) {
    var item;
    item = deployGrid.getItem(row.index);
    if (item.endDate === null) row.customStyles += "color:red;";
    deployGrid.focus.styleRow(row);
    return deployGrid.edit.styleRow(row);
  });
  houseDep = new FilteringSelect({
    id: "houseDepSelect",
    name: "deployment",
    value: "",
    store: deployDataStore,
    searchAttr: "name"
  }, "houseDep");
  houseDep.startup();
  newDep = new Button({
    label: "New",
    onClick: function() {
      return dijit.byId("depDialog").show();
    }
  }, "newDep");
  saveDep = new Button({
    label: "Save",
    onClick: function() {
      return deployDataStore.save();
    }
  }, "saveDep");
  deleteDep = new Button({
    label: "Delete Selected",
    onClick: function() {
      return depDelete();
    }
  }, "deleteDep");
  clearSelectDep = new Button({
    label: "Clear Selection",
    onClick: function() {
      return deployGrid.selection.clear();
    }
  }, "clearDep");
  depAddBtn = new Button({
    label: "Add",
    onClick: function() {
      return addDeployment();
    }
  }, "dlg_addDep");
  depClearBtn = new Button({
    label: "Cancel",
    onClick: function() {
      return clearDeployment();
    }
  }, "dlg_clearDep");
  addDeployment = function() {
    var endDate, startDate, theDesc, theName, theObj;
    console.log("Storing Deployment");
    theName = dijit.byId("depName").value;
    theDesc = dijit.byId("depDesc").value;
    startDate = dijit.byId("depStart").value;
    endDate = dijit.byId("depEnd").value;
    if (theName === "") {
      console.log("Name Must Be Supplied");
      return;
    }
    if (startDate === null || isNaN(startDate.valueOf())) startDate = null;
    if (endDate === null || isNaN(endDate.valueOf())) endDate = null;
    theObj = {
      name: theName,
      description: theDesc,
      startDate: startDate,
      endDate: endDate,
      table: "__Deployment__"
    };
    deployStore.add(theObj);
    return clearDeployment();
  };
  clearDeployment = function() {
    var dlg;
    dlg = dijit.byId("depDialog");
    dlg.reset();
    return dlg.hide();
  };
  depDelete = function() {
    var items, row, _i, _len, _results;
    items = deployGrid.selection.getSelected();
    _results = [];
    for (_i = 0, _len = items.length; _i < _len; _i++) {
      row = items[_i];
      _results.push(deployDataStore.deleteItem(row));
    }
    return _results;
  };
  deployFormatter = function(theItem) {
    var theDep;
    theDep = deployStore.get(theItem);
    return theDep.name;
  };
  houseStore = Cache(Observable(jsonRest({
    target: "rest/house/"
  })), Memory());
  houseGrid = new dataGrid({
    store: houseDataStore = ObjectStore({
      objectStore: houseStore
    }),
    structure: [
      {
        name: "id",
        field: "id",
        width: "50px"
      }, {
        name: "address",
        field: "address",
        width: "200px",
        editable: "true"
      }, {
        name: "startDate",
        field: "startDate",
        width: "150px",
        formatter: dateFormatter,
        editable: true,
        type: dojox.grid.cells.DateTextBox,
        getValue: getDateValue
      }, {
        name: "endDate",
        field: "endDate",
        width: "150px",
        formatter: dateFormatter,
        editable: true,
        type: dojox.grid.cells.DateTextBox,
        getValue: getDateValue
      }, {
        name: "Deployment",
        field: "deploymentId",
        width: "100px",
        editable: true,
        type: dojox.grid.cells._Widget,
        widgetClass: dijit.form.FilteringSelect,
        widgetProps: {
          store: deployDataStore,
          searchAttr: "name"
        },
        formatter: deployFormatter
      }
    ]
  }, "houseGrid");
  houseGrid.startup();
  dojo.connect(houseGrid, 'onStyleRow', houseGrid, function(row) {
    var item;
    item = houseGrid.getItem(row.index);
    if (item.endDate === null) row.customStyles += "color:red;";
    if (item.deploymentId === null) row.customStyles += "color:red;";
    houseGrid.focus.styleRow(row);
    return houseGrid.edit.styleRow(row);
  });
  newHouse = new Button({
    label: "Add",
    onClick: function() {
      return dijit.byId("houseDialog").show();
    }
  }, "newHouse");
  depHouseAddBtn = new Button({
    label: "Add",
    onClick: function() {
      return addHouse();
    }
  }, "dlg_addHouse");
  depHouseClearBtn = new Button({
    label: "Cancel",
    onClick: function() {
      return clearHouse();
    }
  }, "dlg_clearHouse");
  addHouse = function() {
    var deployId, endDate, startDate, theAddress, theObj;
    console.log("Add House");
    theAddress = dijit.byId("houseAdd").value;
    startDate = dijit.byId("houseStart").value;
    endDate = dijit.byId("houseEnd").value;
    deployId = dijit.byId("houseDepSelect").value;
    console.log(deployId);
    if (startDate === null || isNaN(startDate.valueOf())) startDate = null;
    if (endDate === null || isNaN(endDate.valueOf())) endDate = null;
    if (deployId === "") deployId = null;
    theObj = {
      address: theAddress,
      startDate: startDate,
      endDate: endDate,
      deploymentId: deployId,
      table: "__House__"
    };
    console.log(theObj);
    houseStore.add(theObj);
    return clearHouse();
  };
  clearHouse = function() {
    var dlg;
    console.log("Clear Deployment");
    dlg = dijit.byId("houseDialog");
    dlg.reset();
    return dlg.hide();
  };
  houseButton = new Button({
    label: "Save",
    onClick: function() {
      return houseDataStore.save();
    }
  }, "saveHouse");
  resetButton = new Button({
    label: "Reset",
    onClick: function() {
      return houseDataStore.revert();
    }
  }, "resetHouse");
  deleteHouse = new Button({
    label: "Delete Selected",
    onClick: function() {
      return houseDelete();
    }
  }, "deleteHouse");
  clearSelectHouse = new Button({
    label: "Clear Selection",
    onClick: function() {
      return houseGrid.selection.clear();
    }
  }, "clearHouse");
  houseDelete = function() {
    var items, row, _i, _len, _results;
    items = houseGrid.selection.getSelected();
    _results = [];
    for (_i = 0, _len = items.length; _i < _len; _i++) {
      row = items[_i];
      _results.push(houseDataStore.deleteItem(row));
    }
    return _results;
  };
  return console.log("Script Loaded");
});

require(["dojo/store/JsonRest", "dojo/store/Cache", "dojo/store/Observable", "dojo/store/Memory", "dijit/form/Button", "dijit/form/ComboBox", "dijit/form/FilteringSelect", "dijit/Dialog"], function(jsonRest, Cache, Observable, Memory, Button, ComboBox, FilteringSelect) {
  var addRoom, addRoomName, addRoomType, cancelNodeBtn, clearNode, clearRoom, houseSelect, houseStore, locationStore, newRoomBtn, nodeSelect, nodeStore, regNode, regNodeBtn, roomCancelButton, roomNameSelect, roomOkBtn, roomSelect, roomStore, roomTypeSelect, typeStore;
  console.log("PRocessing Dialog");
  nodeStore = Cache(Observable(jsonRest({
    target: "rest/node/"
  })), Memory());
  houseStore = Cache(Observable(jsonRest({
    target: "rest/house/"
  })), Memory());
  roomStore = Cache(Observable(jsonRest({
    target: "rest/room/"
  })), Memory());
  typeStore = Cache(Observable(jsonRest({
    target: "rest/roomtype/"
  })), Memory());
  locationStore = Cache(Observable(jsonRest({
    target: "rest/location/"
  })), Memory());
  nodeSelect = new ComboBox({
    id: "nodeSelect",
    value: "",
    store: nodeStore,
    searchAttr: "id"
  }, "regNodeId");
  houseSelect = new FilteringSelect({
    id: "houseSelect",
    value: "",
    store: houseStore,
    searchAttr: "address"
  }, "regNodeHouse");
  roomSelect = new FilteringSelect({
    id: "roomSelect",
    value: "",
    store: roomStore,
    storeAttr: "name"
  }, "regNodeRoom");
  regNodeBtn = new Button({
    label: "Register",
    onClick: function() {
      return regNode();
    }
  }, "dlg_regNode");
  cancelNodeBtn = new Button({
    label: "Cancel",
    onClick: function() {
      return clearNode();
    }
  }, "dlg_regCancel");
  newRoomBtn = new Button({
    label: "New Room",
    onClick: function() {
      return dijit.byId("roomDialog").show();
    }
  }, "dlg_regNewRoom");
  regNode = function() {
    var houseId, node, nodeId, roomId;
    console.log("Registering Node");
    nodeId = nodeSelect.value;
    houseId = houseSelect.value;
    roomId = roomSelect.value;
    if (nodeId === "" || houseId === "" || roomId === "") {
      dijit.byId("regDialog").validate();
      console.log("WARNING: Missing Data");
      return;
    }
    node = nodeSelect.item;
    console.log("Node is: ", nodeId, " -> ", node);
    console.log("Checking for location ", houseId, " ", roomId);
    return locationStore.query({
      "houseId": houseId,
      "roomId": roomId
    }).then(function(obj) {
      var theObj;
      console.log("Return ", obj);
      if (obj.length > 0) {
        console.log("Location Exists", obj[0].id);
        node.locationId = obj[0].id;
        console.log("The Node ", node);
        nodeStore.put(node);
        return clearNode();
      } else {
        console.log("Adding New Location ", houseId, " ", roomId);
        theObj = {
          id: null,
          houseId: houseId,
          roomId: roomId,
          table: "__location__"
        };
        console.log("New Loc: ", theObj);
        return locationStore.put(theObj).then(function(theLocation) {
          console.log("Added Location");
          console.log("New Location is", theLocation);
          node.locationId = theLocation;
          nodeStore.put(node);
          return clearNode();
        });
      }
    });
  };
  clearNode = function() {
    var dlg;
    dlg = dijit.byId("regDialog");
    dlg.reset();
    return dlg.hide();
  };
  roomNameSelect = new ComboBox({
    id: "roomNameSelect",
    value: "",
    store: roomStore,
    storeAttr: "name"
  }, "newRoomRoom");
  roomTypeSelect = new ComboBox({
    id: "roomTypeSelect",
    value: "",
    store: typeStore,
    storeAttr: "name"
  }, "newRoomType");
  roomOkBtn = new Button({
    label: "Add",
    onClick: function() {
      return addRoom();
    }
  }, "dlg_roomOk");
  roomCancelButton = new Button({
    label: "Cancel",
    onClick: function() {
      return clearRoom();
    }
  }, "dlg_roomCancel");
  addRoomType = function() {
    var roomType, tempObj, theObj;
    roomType = roomTypeSelect.item;
    if (roomType) {
      console.log("Using Existing Room Type: ", roomType);
      return addRoomName(roomType.id);
    } else {
      theObj = {
        id: null,
        name: roomTypeSelect.getValue(),
        __table__: "RoomType"
      };
      console.log("Add New Room Type:", theObj);
      return tempObj = typeStore.add(theObj).then(function(obj) {
        return addRoomName(obj);
      });
    }
  };
  addRoomName = function(typeId) {
    var roomItem, theObj;
    console.log("Dealing with room Name");
    console.log("Room Type Id: ", typeId);
    roomItem = roomNameSelect.item;
    if (roomItem) {
      console.log("Using Existing Room Type: ", roomItem);
    } else {
      theObj = {
        id: null,
        name: roomNameSelect.getValue(),
        roomTypeId: typeId,
        __table__: "Room"
      };
      return roomStore.add(theObj);
    }
  };
  addRoom = function() {
    addRoomType();
    return clearRoom();
  };
  return clearRoom = function() {
    var dlg;
    dlg = dijit.byId("roomDialog");
    dlg.reset();
    return dlg.hide();
  };
});

setNodeId = function(nodeId) {
  var dropDown, theStore;
  console.log("Attempting to set node Id ", nodeId);
  dropDown = dijit.byId("nodeSelect");
  console.log("Dropdown is ", dropDown);
  theStore = dropDown.store;
  return theStore.query({
    id: nodeId
  }).then(function(item) {
    console.log("Query Items ", item[0]);
    dropDown.set('value', item[0].id);
    dropDown.item = item[0];
    return console.log("Done");
  });
};
