require(
    ["dojo/topic"],
    (topic) ->
        console.log("Topic Fired")
        topic.subscribe("navTree", (arg1) ->
                console.log("--- FIRED --- ",arg1)
            )
    )
