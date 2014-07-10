<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>

<%block name="pageheader">
<h1>Server Status</h1>
</%block>

<%block name="pagecontent">
<section>
  <h2>Daemon Status</h2>
  <ul>
    %if chsf == 0:
        <li>ch-sf: <strong class="text-success"><i class="icon-ok"></i>Running</strong></li>
    %else:
        <li>ch-sf: <strong class="text-error"><i class="icon-warning-sign"></i> Error: ${chsf}</strong></li>
    %endif  
    
    %if chbase == 0:
        <li>ch-base: <strong class="text-success"><i class="icon-ok"></i>Running</strong></li>
    %else:
        <li>ch-base: <strong class="text-error"><i class="icon-warning-sign"></i> Error: ${chbase}</strong></li>
    %endif  

   %if logpass:
	<li>Logging: <strong class="text-success"><i class="icon-ok"></i>Running</strong></li>
    %else:
        <li>Logging: <strong class="text-error"><i class="icon-warning-sign"></i> Error</strong></li>
    %endif  
  </ul>

  %if logpass:
  <h4>BaseLog Tail</h4>
  ${logtail | n}
  %endif
  

</section>

<section>
  <h2>Network Status:</h2>
  <p>Can Connect to Cogentee: 
    %if ping == 0:
        <strong class="text-success"><i class="icon-ok"></i>Yes</strong>
    %else:
	<strong class="text-error"><i class="icon-warning-sign"></i> Error</strong></li>
    %endif
    
  <h3>Network Interfaces</h3>
  ${ifconfig | n}
</section>

</%block>
