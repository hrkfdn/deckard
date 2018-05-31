let hooks = undefined;

function addHook(hook, hash) {

}

function populateHooks() {
    const hookTree = {};

    $.ajax("/hooks", {
        success: function(data, textStatus, jqXHR) {
            $.each(data, function(index, value) {
                const hook = value;
                const hash = index;

                if(!_.has(hookTree, hook.classname)) {
                    _.set(hookTree, hook.classname, [hook]);
                }
                else {
                    // hook directory already has hooks for this class
                    // -> merge this class into it
                    const current = _.get(hookTree, hook.classname);
                    console.log(hook.classname, current);
                    const merged = current.concat([hook]);
                    _.set(hookTree, hook.classname, merged);
                }
            });
        }
    });

    console.log(hookTree);
}

$(document).ready(function() {
    hooks = $("#hookstree");

    //populateHooks();
});