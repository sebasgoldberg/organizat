message = {}

message.check_continue = function(text, callback){
    dhtmlx.message({
        type:"confirm-warning", 
        text:text,
        callback: function(result){
            if (!result)
                return;
            callback();
        }
    });
};

message.error = function(errors){
    for (var i=0; i<errors.length; i++){
        error = errors[i];
        dhtmlx.message({ type:"error", text:error, expire: -1});
    }
};

message.info = function(infos){
    for (var i=0; i<infos.length; i++){
        info = infos[i];
        dhtmlx.message({text:info, expire: -1});
    }
};

