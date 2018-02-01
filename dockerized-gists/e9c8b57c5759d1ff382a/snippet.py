# Example from http://jakevdp.github.io/blog/2013/06/01/ipython-notebook-javascript-python-communication/ adapted for IPython 2.0
# Add an input form similar to what we saw above

from IPython.display import HTML
from math import pi, sin

input_form = """
<div style="background-color:gainsboro; border:solid black; width:600px; padding:20px;">
Code: <input type="text" id="code_input" size="50" height="2" value="sin(pi / 2)"><br>
Result: <input type="text" id="result_output" size="50" value="1.0"><br>
<button onclick="exec_code()">Execute</button>
</div>
"""
 
# here the javascript has a function to execute the code
# within the input box, and a callback to handle the output.
javascript = """
<script type="text/Javascript">
   function handle_output(out){
//       console.log(out_type);
       console.log(out);
       var res = null;
        // if output is a print statement
       if(out.msg_type == "stream"){
           res = out.content.data;
       }
       // if output is a python object
       else if(out.msg_type === "execute_result"){
           res = out.content.data["text/plain"];
       }
       // if output is a python error
       else if(out.msg_type == "pyerr"){
           res = out.content.ename + ": " + out.content.evalue;
       }
       // if output is something we haven't thought of
       else{
           res = "[out type not implemented]";  
       }
       document.getElementById("result_output").value = res;
   }
   
   function exec_code(){
       var code_input = document.getElementById('code_input').value;
       var kernel = IPython.notebook.kernel;
       var callbacks = { 'iopub' : {'output' : handle_output}};
       document.getElementById("result_output").value = "";  // clear output box
       var msg_id = kernel.execute(code_input, callbacks, {silent:false});
       console.log("button pressed");
       // IPython.notebook.clear_output();
   }
</script>
"""
 
HTML(input_form + javascript)