<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>



<%block name="pageheader">
<h1>Login</h1>
</%block>

<%block name="pagecontent">
<div class="span4 offset4">
##<h2>You need to be logged in to view this page</h2>

<div class="well">
  <legend>Login</legend>
  %if loginMsg:
      <div class="alert alert-error" data-dismiss="alert">
	<strong>Login Error:</strong> ${loginMsg}
      </div>
  %endif

  <form method="POST" action="" accept-charset="UTF-8" class="form-horizontal">
    <div class="control-group">
      <label class="control-label" for="username">Username</label>
      <div class="controls">
	<div class="input-prepend">
	  <span class="add-on"><i class="icon-user"></i></span>
	  <input class="span12" placeholder="Username" name="username" required="true">
	</div>
      </div>
    </div>
    
    <div class="control-group">
      <label class="control-label" for="password">Password</label>
      <div class="controls">
	<div class="input-prepend">
	  <span class="add-on"><i class="icon-key"></i></span>
	  <input class="span12" placeholder="Password" type="password" name="password" required="true"> 
	</div>
      </div>
    </div>
    <button class="btn-info btn" type="submit" name="submit">Login</button>      
  </form>    
</div>

</div>
</%block>


