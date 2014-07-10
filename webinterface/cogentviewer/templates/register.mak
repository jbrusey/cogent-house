<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>



<%block name="pageheader">
<h1>Register New User</h1>
</%block>

<%block name="pagecontent">
<div class="span6 offset3">

<div class="well">
  <legend>Register User</legend>
  %if loginMsg:
      <div class="alert alert-error" data-dismiss="alert">
	<strong>Error:</strong> ${loginMsg}
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
      <label class="control-label" for="email">Email</label>
	  <div class="controls">
	    <div class="input-prepend">
	      <span class="add-on"><i class="icon-envelope"></i></span>
	      <input class="span12" placeholder="foo@bar.net" name="email" type="email" required="true">
	    </div>
	  </div>
    </div>
    
    <div class="control-group">
      <label class="control-label" for="password">Password</label>
      <div class="controls">
	<div class="input-prepend">
	  <span class="add-on"><i class="icon-key"></i></span>
	  <input class="span12" placeholder="Password" type="password" name="password" required="true" id="password"> 
	</div>
      </div>
    </div>

    <div class="control-group" id="passCheckGrp">
      <label class="control-label" for="passCheck">Repeat Password</label>
      <div class="controls">
	<div class="input-prepend">
	  <span class="add-on"><i class="icon-repeat"></i></span>
	  <input class="span12" placeholder="Password" type="password" name="passwordCheck" required="true" id="passwordCheck"> 
	</div>
      </div>
      <span class="help-inline" id="passHelp"></span>
    </div>   

    <button class="btn-info btn" type="submit" name="submit">Register</button>   
</form>    
</div>

</div>
</%block>



<%block name="scripts">
<script src="${request.static_url('cogentviewer:static/scripts/signup.js')}"></script>
</%block>
