var hooks = undefined;

function addHook(hook, hash) {

}

function populateHooks() {
    var hookTree = {};

    $.ajax("/hooks", {
        success: function(data, textStatus, jqXHR) {
            $.each(data, function(index, value) {
                var hook = value;
                var hash = index;

                if(!_.has(hookTree, hook.classname)) {
                    _.set(hookTree, hook.classname, [hook]);
                }
                else {
                    // hook directory already has hooks for this class
                    // -> merge this class into it
                    var current = _.get(hookTree, hook.classname);
                    console.log(hook.classname, current);
                    var merged = current.concat([hook]);
                    _.set(hookTree, hook.classname, merged);
                }
            });
        }
    });

    console.log(hookTree);
}

$(document).ready(function() {
    hooks = $("#hookstree");

    populateHooks();
});