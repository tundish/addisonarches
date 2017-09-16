<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>{{info.get("title", "Addison Arches")}}</title>
<link rel="stylesheet" href="/css/pure/base-min.css" />
<link rel="stylesheet" href="/css/pure/pure-min.css" media="screen" />
<link rel="stylesheet" href="/css/pure/grids-responsive-min.css" media="screen" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
</head>
<body>
<%  
    projpath = info["args"].get("output", "#")
    steps = [i for i in items.items() if i[1].__class__.__name__ == "Invocation"]
 %>
<div class="pure-g">
    <div class="pure-u-1-2 pure-u-lg-7-12">
    </div>
    <div class="pure-u-1-2 pure-u-lg-5-12">
        <div class="pure-menu pure-menu-open pure-menu-horizontal">
        <ul>
            <li><a href="file://{{projpath}}">My Files</a></li>
            <li><a href="#">Documentation</a></li>
            <li><a href="#">Support</a></li>
        </ul>
        </div>
    </div>
</div>
<div class="pure-g">
    <div class="pure-u-1-2 pure-u-lg-3-24">
        <div class="pure-menu pure-menu-open">
            <a class="pure-menu-heading">Workflow</a>

            <ul>
                %   for id, step in steps:
                <li><a href="#{{id}}">
                {{step.target.replace('_', ' ').capitalize()}}
                </a></li>
                %   end
                <li class="pure-menu-heading">Plots</li>
                <li><a href="#">Map</a></li>
            </ul>
        </div>
    </div>
    <div class="pure-u-1-2 pure-u-lg-16-24">
    %   for id, step in steps:
        <form class="pure-form pure-form-aligned" method="post" action="#">
            <fieldset>
                <input type="hidden"
                name="_type" value="{{step.__class__.__name__}}" />
                <input type="hidden"
                name="target" value="{{step.target}}" />
                %   for arg in step.args:
                <div class="pure-control-group">
                    <label for="{{arg.name}}">{{arg.name}}</label>
                    <input id="{{arg.name}}" type="text"
                    name="{{arg.name}}"
                    pattern="{{arg.regex.pattern}}"
                    placeholder="{{arg.value}}" />
                    <label for="{{arg.name}}">{{arg.unit}}</label>
                </div>
                %   end
                <div class="pure-controls">
                    <button type="submit"
                    class="pure-button pure-button-primary">Go</button>
                </div>
            </fieldset>
        </form>
    %   end
    </div>
</div>
</body>
</html>
