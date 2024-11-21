using Agents, Random, Distributions,HTTP,JSON



# Define el agente de Caja
@agent struct BoxAgent(GridAgent{3})
    width::Int
    height::Int
    depth::Int
    weight::Int
    position_in_container::Tuple{Float64, Float64, Float64}  # Posición en el contenedor
    showing::Int = 1
end

# Define el agente de Robot
@agent struct RobotAgent(GridAgent{3})
    min_x::Int  # Límite izquierdo del carril
    max_x::Int  # Límite derecho del carril
    drop_zone_x::Int
    drop_zone_z::Int 
    collect_zone_z::Int  
    heading_back::Bool = false  # Indicador de si el robot está regresando al stack
    cargo_boxes::Vector{Any} = []  # Lista de cajas transportadas
    is_working::Bool = true  # Indicador de si el robot está trabajando
    previous_pos::Tuple{Int, Int,Int} # Posición anterior
    direction::String = ""
    rotating::Int = 0
    previous_direction::String = "RIGHT"
    timer::Int = 0
    just_changed_lanes::Bool = false
    one_time_rotation::Int = 1
    actual_x::Int
    getting_back_to_lane::Bool = false
    new_pos::Tuple{Int,Int,Int} = (0,0,0)
    box_width::Int = 0
    box_height::Int = 0
    box_depth::Int = 0
end

function agent_step!(agent, model)
    if agent isa RobotAgent
        robot_step!(agent, model)
    elseif agent isa BoxAgent
        box_step!(agent, model)
    end
end

# Función sin operación para las cajas (ya que no se mueven)
function box_step!(box::BoxAgent, model) end

# Función principal de movimiento y operación de los robots
function robot_step!(robot::RobotAgent, model)
    if robot.rotating == 0
        if !robot.heading_back
            # Si el robot tiene cajas pendientes y está trabajando, comienza su recorrido a buscar caja
            if !isempty(robot.cargo_boxes) && robot.is_working
                if at_collect_zone(robot) 
                    # el robot  esta en la posicion en z de recogida de paquetes. 
                    if !isempty(robot.cargo_boxes) && robot.cargo_boxes[1].pos[1] != robot.pos[1]
                        if robot.pos[1] > robot.cargo_boxes[1].pos[1]
                            robot.new_pos = (robot.pos[1] - 1, robot.pos[2],robot.pos[3])
                        elseif robot.pos[1] < robot.cargo_boxes[1].pos[1]
                            robot.new_pos = (robot.pos[1] + 1, robot.pos[2],robot.pos[3])
                        end
                    else
                        #Aqui el robot esta en la posicion de la caja a recoger entonces se apica la logica
                        collect_box!(robot) 
                    end
                else
                    # el robot no esta en la posicion en z de recogida de paquetes. 
                    if robot.pos[1] < 20
                        robot.new_pos = (robot.pos[1] + 1, robot.pos[2],robot.pos[3])
                    elseif robot.pos[1] > 20
                        robot.new_pos = (robot.pos[1] - 1, robot.pos[2],robot.pos[3])
                    elseif robot.pos[3] < robot.collect_zone_z
                        robot.new_pos = (robot.pos[1], robot.pos[2],robot.pos[3] + 1)
                    elseif robot.pos[3] > robot.collect_zone_z
                        robot.new_pos = (robot.pos[1], robot.pos[2],robot.pos[3] - 1)
                    end
                end
            end
        else
            if robot.pos[1] != 20 && robot.pos[3] != robot.drop_zone_z
                if robot.pos[1] < 20 
                    robot.new_pos = (robot.pos[1] + 1, robot.pos[2],robot.pos[3])
                elseif robot.pos[1] > 20
                    robot.new_pos = (robot.pos[1] - 1, robot.pos[2],robot.pos[3])
                end 
            elseif robot.pos[1] == 20 && robot.pos[3] > robot.drop_zone_z
                robot.new_pos = (robot.pos[1], robot.pos[2],robot.pos[3] - 1)
            elseif robot.pos[3] == robot.drop_zone_z && robot.pos[1] != robot.drop_zone_x
                robot.new_pos = (robot.pos[1] + 1, robot.pos[2],robot.pos[3])
            elseif at_drop_zone(robot)  # Si está en el área de drop zone
                drop_box(robot, model)  # Dejar la caja en el stack
                robot.heading_back = false  # Volver al modo de búsqueda de cajas
                if isempty(robot.cargo_boxes)
                    robot.is_working = false
                end
            end
        end
        if !check_for_rotation(robot)
            robot.previous_direction = robot.direction
            robot.previous_pos = robot.pos  
            robot.pos = robot.new_pos
        end
    else
        if robot.one_time_rotation == 1
            robot.one_time_rotation -= 1
        end
        if robot.timer > 0
            robot.timer -= 1
            println("Robot $(robot.id) en rotación con timer $(robot.timer)")
        else
            robot.rotating = 0
            robot.one_time_rotation = 1
            robot.previous_direction = robot.direction
            println("Robot $(robot.id) ha completado la rotación.")
        end
    end
end

function check_for_rotation(robot::RobotAgent)
    if robot.new_pos != robot.pos
        delta = (robot.new_pos[1] - robot.pos[1], robot.new_pos[3] - robot.pos[3])
        robot.direction = get_direction(delta)
    end
    if robot.direction != robot.previous_direction
        robot.rotating = 1
        if (robot.direction == "LEFT" && robot.previous_direction == "RIGHT") || 
            (robot.direction == "RIGHT" && robot.previous_direction == "LEFT") ||
            (robot.direction == "UP" && robot.previous_direction == "DOWN") || 
            (robot.direction == "DOWN" && robot.previous_direction == "UP")
            robot.timer = 12
        else        
            robot.timer = 6
        end
        return true
    else
        return false
    end
end

# Función para actualizar la rotación del robot
function update_direction(robot::RobotAgent)
    if robot.pos != robot.previous_pos
        delta = (robot.pos[1] - robot.previous_pos[1], robot.pos[3] - robot.previous_pos[3])
        robot.direction = get_direction(delta)
        robot.previous_pos = robot.pos
    end
end

# Determina la dirección de la rotación basada en el delta de movimiento
function get_direction(delta::Tuple{Int, Int})
    return delta == (1, 0) ? "RIGHT" :
           delta == (-1, 0) ? "LEFT" :
           delta == (0, 1) ? "DOWN" : "UP"
end

# Comprueba si el robot está en la posición de la caja
function at_box_position(robot::RobotAgent, box::BoxAgent)
    return robot.pos == (box.pos[1], box.pos[2] - 1)
end

# Comprueba si el robot está en la zona de descarga
function at_drop_zone(robot::RobotAgent)
    return robot.pos == (robot.drop_zone_x, 1,robot.drop_zone_z)
end

function at_collect_zone(robot::RobotAgent)
    return robot.pos[3] == robot.drop_zone_z
end

# Función para recoger una caja
function collect_box!(robot::RobotAgent)
    robot.heading_back = true       # Señalar que el robot debe regresar al contenedor
    box = robot.cargo_boxes[1]
    box.showing = 0
    robot.box_width = box.width
    robot.box_height = box.height
    robot.box_depth = box.depth
    println("Robot $(robot.id) recogió una caja en posición $(box.pos)")
end

# Actualiza la matriz eliminando la caja recolectada
function update_matrix!(model, box)
    matrix = model.matrix
    matrix[box.pos[1], box.pos[2]] = 1  # Marcar la posición de la caja como vacía en la matriz
    model.matrix = matrix
end


# El robot deja la caja en la estantería
function drop_box(robot::RobotAgent, model)
    robot.heading_back = false  # Marcar que el robot no está regresando
    box = robot.cargo_boxes[1]
    move_agent!(box, model, (box.position_in_container[1] + 20, box.position_in_container[2], box.position_in_container[3] + 40))
    box.showing = 1
    popfirst!(robot.cargo_boxes)
    robot.box_width = 0
    robot.box_height = 0
    robot.box_depth = 0
    println("Robot $(robot.id) dejó una caja en el contenedor")
end 

function send_packing_request(api_url, packing_data)
    response = HTTP.post(api_url, headers = ["Content-Type" => "application/json"], body = JSON.json(packing_data))  
    if response.status == 200
        println("Packing request successful")
        return JSON.parse(String(response.body))
    else
        error("Packing request failed with status: $(response.status)")
    end
end

function generate_packing_data(container, items)
    return Dict(
        "box" => [
            Dict(
                "name" => container[:name],
                "WHD" => container[:WHD],
                "weight" => container[:weight],
                "coner" => container[:corner],
                "openTop" => [container[:openTop]]
            )
        ],
        "item" => [Dict(
            "name" => item[:name],
            "WHD" => item[:WHD],
            "weight" => item[:weight],
            "count" => item[:count],
            "level" => item[:level],
            "loadbear" => item[:loadbear],
            "updown" => item[:updown],
            "color" => item[:color],
            "type" => item[:type]
        ) for item in items],
        "binding" => []  # Si tienes datos de vinculación, agrégalos aquí
    )
end

function handle_packing(api_url, container, items, model)
    packing_data = generate_packing_data(container, items)
    packing_result = send_packing_request(api_url, packing_data)
    if packing_result["Success"]
        robots = [agent for agent in allagents(model) if agent isa RobotAgent]

        # Verificar si hay robots disponibles
        if isempty(robots)
            println("No hay robots disponibles en el modelo.")
            return
        end

        robot_index = 1
        start_x = 5
        # Agregar cajas al modelo
        for item in packing_result["data"]["fitItem"]
            end_pos = Tuple(item["position"])
            dimensions = Tuple(item["WHD"])
            weight = item["weight"]
            # Asignar posición inicial (simulada aleatoriamente)
            start_pos = (start_x, 1, 80)
            
            box = add_agent!(BoxAgent,
                model;
                pos = start_pos,
                weight = weight,
                width = dimensions[1],
                height = dimensions[2],
                depth = dimensions[3],
                position_in_container = end_pos
            )
            # Asignar la caja al cargo_boxes del robot actual
            push!(robots[robot_index].cargo_boxes, box)

            # Avanzar al siguiente robot (ciclo circular)
            robot_index = robot_index % length(robots) + 1
            start_x = start_x + box.height + 3
        end

        println("Cajas agregadas al modelo después de ordenarlas.")
    else
        println("Error al ordenar las cajas: ", response_data["Reason"])
    end
    
end

# Función para inicializar el modelo sin *pathfinding*
function warehouse_simulation(; grid_dims = (200,50,200), num_boxes = 5)
    container = Dict(:name => "Container1", :WHD => [40, 60, 15], :weight => 1000, :corner => [0, 0, 0], :openTop => 1)
    items = [
    Dict(:name => "Box1", :WHD => [10, 10, 10], :weight => 5, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box2", :WHD => [20, 20, 20], :weight => 10, :count => 2, :level => 1, :loadbear => 20, :updown => 1, :color => 2, :type => 1)
    ]
    space = GridSpace((200,40,200); periodic = false, metric = :chebyshev)
    model = StandardABM(Union{RobotAgent, BoxAgent}, space; agent_step! = agent_step!, scheduler = Schedulers.Randomly(), properties = Dict{Symbol, Any}(:matrix => nothing))
    initialize_robots!(model)
    handle_packing("http://192.168.1.85:5050/calPacking", container, items, model)
    return model
end

# # Inicializa la matriz y coloca cajas en posiciones aleatorias
# function initialize_grid!(model, grid_dims, num_boxes)
#     matrix = fill(1, grid_dims)
#     for a in 1:num_boxes
#         empty = collect(empty_positions(model))
#         pos = rand(empty)
#         x, z = pos[1], pos[3]
#         while z == 1 || z == 2  # Evita la zona de descarga y de robots
#             pos = rand(empty)
#             x, z = pos[1], pos[3]
#         end
#         matrix[x, z] = 0  # Marca la posición de la caja en la matriz
#         add_agent!(BoxAgent, model; pos = pos, id = a + 100)
#     end
#     model.matrix = matrix
# end

# Inicializa los robots y define los límites de cada uno en el almacén
function initialize_robots!(model)
    # coordinates = [(1, 3, 1, 8), (9, 3, 9, 16), (17, 3, 17, 24), (25, 3, 25, 32), (33, 3, 33, 40)]
    # for (id, (x, z, min_x, max_x)) in enumerate(coordinates)
    #     robot = add_agent!(RobotAgent, model; pos = (x, z), min_x = min_x, max_x = max_x, drop_zone_x = min_x, id = id, actual_x = x, previous_pos = (x,z))
    # end
    x = 20
    z = 40
    add_agent!(RobotAgent, model; pos = (x,1,z), min_x = 5, max_x = 20, drop_zone_x = 40,drop_zone_z = 40, collect_zone_z = 80,id = 1, actual_x = x, previous_pos = (x,1,z))
end

# Carga las cajas en la ruta del robot (sin necesidad de *pathfinding*)
function load_cargo!(robot::RobotAgent, model)
    for y in 3:40, x in robot.min_x:robot.max_x
        box = collect(agents_in_position((x, y), model))
        if !isempty(box)
            push!(robot.cargo_boxes, box[1])
        end
    end
end

# Función para verificar si una posición está dentro de los límites
function in_bounds(pos, grid_dims)
    return 1 <= pos[1] <= grid_dims[1] && 1 <= pos[2] <= grid_dims[2]
end
