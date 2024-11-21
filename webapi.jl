include("warehouse.jl")
using Genie, Genie.Renderer.Json, Genie.Requests, HTTP
using UUIDs

# Diccionario para almacenar instancias de simulaciones con IDs únicos
instances = Dict()

# Ruta para crear una nueva simulación de almacén
route("/simulations", method = POST) do
    payload = jsonpayload()
    model = warehouse_simulation()  # Inicializa una nueva instancia de simulación
    id = string(uuid1())  # Genera un ID único para la simulación
    instances[id] = model  # Guarda el modelo en el diccionario

    robots = []
    boxes = []
    bins = []

    # Recorre los agentes y organiza los datos de robots y cajas para responder al cliente
    for agent in allagents(model)
        if agent isa RobotAgent
            push!(robots, Dict(
                "id" => agent.id,
                "position" => collect(agent.pos),
                "is_working" => agent.is_working,
                "cargo_count" => length(agent.cargo_boxes),
                "direction" => agent.direction,
                "rotating" => agent.rotating,
                "previous_direction" => agent.previous_direction,
                "one_time_rotation" => agent.one_time_rotation,
                "box_width" => agent.box_width,
                "box_height" => agent.box_height,
                "box_depth" => agent.box_depth
            ))
        elseif agent isa BoxAgent
            push!(boxes, Dict(
                "id" => agent.id,
                "position" => collect(agent.pos),
                "showing" => agent.showing,
                "WHD" => [agent.width,agent.height,agent.depth]
            ))
        end
    end

    # Devuelve la respuesta JSON con el ID de la simulación y el estado inicial de los agentes
    json(Dict("Location" => "/simulations/$id", "robots" => robots, "boxes" => boxes))
end

# Ruta para obtener el estado de una simulación específica y avanzar un paso en la simulación
route("/simulations/:id") do
    # id = params(:id)
    model = instances[payload(:id)]  # Recupera el modelo de simulación con el ID dado

    # Avanza la simulación un paso
    run!(model, 1)

    robots = []
    boxes = []

    # Recorre los agentes y organiza los datos de robots y cajas después de avanzar un paso
    for agent in allagents(model)
        if agent isa RobotAgent
            push!(robots, Dict(
                "id" => agent.id,
                "position" => collect(agent.pos),
                "is_working" => agent.is_working,
                "cargo_count" => length(agent.cargo_boxes),
                "direction" => agent.direction,
                "rotating" => agent.rotating,
                "previous_direction" => agent.previous_direction,
                "one_time_rotation" => agent.one_time_rotation,
                "box_width" => agent.box_width,
                "box_height" => agent.box_height,
                "box_depth" => agent.box_depth
            ))
        elseif agent isa BoxAgent
            push!(boxes, Dict(
                "id" => agent.id,
                "position" => collect(agent.pos),
                "showing" => agent.showing,
                "WHD" => [agent.width,agent.height,agent.depth]
            ))
        end
    end

    # Devuelve la respuesta JSON con el estado actualizado de los robots y cajas
    json(Dict("robots" => robots, "boxes" => boxes))
end

# Configuraciones de CORS para permitir acceso desde cualquier origen y varios métodos HTTP
Genie.config.run_as_server = true
Genie.config.cors_headers["Access-Control-Allow-Origin"] = "*"
Genie.config.cors_headers["Access-Control-Allow-Headers"] = "Content-Type"
Genie.config.cors_headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
Genie.config.cors_allowed_origins = ["*"]

# Inicia el servidor web
up(8000, "0.0.0.0")