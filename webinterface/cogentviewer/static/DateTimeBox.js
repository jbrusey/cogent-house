define([
	"dojo/_base/declare",
	'dojo/_base/lang',
	'dojo/date/locale',
    'dojox/grid/cells/dijit'
], function (declare, lang, locale) {
	return declare('DateTextBox', dojox.grid.cells.DateTextBox, { 
		setValue: function(inRowIndex, inValue){
	    	if (this.widget){ 
	    		// this.widget.set('value', new Date(inValue)); // This was
		    //decremending the day for some reason with yyyy-MM-dd dates 
	            this.widget.set('value', locale.parse(inValue, {selector:
								    'date', datePattern: 'yyyy-MM-dd'})); 
	        } else { 
	            this.inherited(arguments); 
	        }
	    },
	    getWidgetProps: function(inDatum){
	    	return lang.mixin(this.inherited(arguments), {
	            //value: new Date(inDatum) // This was decremending the day for
		    //some reason with yyyy-MM-dd dates 
	            value: locale.parse(inDatum, {selector: 'date', datePattern:
						  'yyyy-MM-dd'})
	        });
	    }
	});
});