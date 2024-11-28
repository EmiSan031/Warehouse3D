using Agents, Random, Distributions,HTTP,JSON

# Define el agente de Caja
@agent struct BoxAgent(GridAgent{3})
    width::Int
    height::Int
    depth::Int
    weight::Int
    position_in_container::Tuple{Int, Int, Int}  # Posición en el contenedor
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
    one_time_rotation::Int = 1
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
function box_step!(box::BoxAgent, model) 
    println("Caja $(box.id) con posicion $(box.pos)")

end

# Función principal de movimiento y operación de los robots
function robot_step!(robot::RobotAgent, model)
    if robot.rotating == 0
        if !robot.heading_back
            # Si el robot tiene cajas pendientes y está trabajando, comienza su recorrido a buscar caja
            if !isempty(robot.cargo_boxes) && robot.is_working
                if at_collect_zone(robot) || robot.pos[3] == robot.collect_zone_z + 1
                    # el robot  esta en la posicion en z de recogida de paquetes. 
                    if !isempty(robot.cargo_boxes) && robot.cargo_boxes[1].pos[1] != robot.pos[1]   
                        if robot.pos[1] > robot.cargo_boxes[1].pos[1]
                            robot.new_pos = (robot.pos[1] - 1, robot.pos[2],robot.pos[3])
                        elseif robot.pos[1] < robot.cargo_boxes[1].pos[1]
                            robot.new_pos = (robot.pos[1] + 1, robot.pos[2],robot.pos[3])
                        end
                    elseif robot.cargo_boxes[1].pos[1] == robot.pos[1] && robot.pos[3] != robot.collect_zone_z + 1
                        robot.new_pos = (robot.pos[1], robot.pos[2],robot.pos[3]+1)#Aqui el robot esta en la posicion de la caja a recoger entonces se apica la logica
                    else
                        collect_box!(robot) 
                    end
                else
                    # el robot no esta en la posicion en z de recogida de paquetes. 
                    if robot.pos[1] < 0
                        robot.new_pos = (robot.pos[1] + 1, robot.pos[2],robot.pos[3])
                    elseif robot.pos[1] > 0
                        robot.new_pos = (robot.pos[1] - 1, robot.pos[2],robot.pos[3])
                    elseif robot.pos[3] < robot.collect_zone_z
                        robot.new_pos = (robot.pos[1], robot.pos[2],robot.pos[3] + 1)
                    elseif robot.pos[3] > robot.collect_zone_z
                        robot.new_pos = (robot.pos[1], robot.pos[2],robot.pos[3] - 1)
                    end
                end
            end
            if !robot.is_working
                if robot.pos[3] != 1 
                    robot.new_pos = (robot.pos[1], robot.pos[2],robot.pos[3] - 1)
                elseif robot.pos[3] == 1 && robot.pos[1] != 1
                    robot.new_pos = (robot.pos[1] - 1, robot.pos[2],robot.pos[3])
                end
            end
        else
            if robot.pos[3] != 80 && robot.pos[1] != 30 && robot.pos[3] != robot.drop_zone_z
                robot.new_pos = (robot.pos[1], robot.pos[2],robot.pos[3] - 1)
            elseif robot.pos[1] != 30 && robot.pos[3] != robot.drop_zone_z
                if robot.pos[1] < 30 
                    robot.new_pos = (robot.pos[1] + 1, robot.pos[2],robot.pos[3])
                elseif robot.pos[1] > 30
                    robot.new_pos = (robot.pos[1] - 1, robot.pos[2],robot.pos[3])
                end 
            elseif robot.pos[1] == 30 && robot.pos[3] > robot.drop_zone_z
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
            if !robot_in_front(robot,model) && !robot_in_dropzone(robot,model)
                robot.pos = robot.new_pos
            end
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
function in_position(pos::Tuple{Int, Int, Int}, model)
    return !isempty(agents_in_position(pos, model))
end

function robot_in_dropzone(robot::RobotAgent,model)
    if robot.pos[3] == 80 && robot.pos[1] == 31
        for neighbor in nearby_agents(robot, model, 50)
            if neighbor isa RobotAgent
                if neighbor.pos[3] == robot.drop_zone_z
                    return true
                end
            end
        end
        return false
    end
    return false
end
function robot_in_front(robot::RobotAgent,model)
    for neighbor in nearby_agents(robot, model, 60)
        if neighbor isa RobotAgent
            if robot.direction == "RIGHT"
                if (neighbor.pos[1] > robot.pos[1] && neighbor.pos[1] < robot.pos[1] + 60) && (neighbor.pos[3] > robot.pos[3] - 10 && neighbor.pos[3] < robot.pos[3] + 10)
                    return true
                else
                    return false
                end
            elseif robot.direction == "LEFT"
                if (neighbor.pos[1] < robot.pos[1] && neighbor.pos[1] > robot.pos[1] - 60) && (neighbor.pos[3] > robot.pos[3] - 10 && neighbor.pos[3] < robot.pos[3] + 10)
                    return true
                else
                    return false
                end
            elseif robot.direction == "UP"
                if (neighbor.pos[3] < robot.pos[3] && neighbor.pos[3] > robot.pos[3] - 60) && (neighbor.pos[1] > robot.pos[1] - 10 && neighbor.pos[1] < robot.pos[1] + 10)
                    return true
                else
                    return false
                end
            elseif robot.direction == "DOWN"
                if (neighbor.pos[3] > robot.pos[3] && neighbor.pos[3] < robot.pos[3] + 60) && (neighbor.pos[1] > robot.pos[1] - 10 && neighbor.pos[1] < robot.pos[1] + 10)
                    return true
                else
                    return false
                end
            end
        end
    end
    return false
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
    return robot.pos[3] == robot.collect_zone_z
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
    move_agent!(box,(104 - box.position_in_container[1], box.position_in_container[3], box.position_in_container[2]+20),model)
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
    print(packing_result)
    # Directorio de trabajo actual
    current_folder = pwd()
        
    # Guardar el resultado en un archivo JSON
    file_path = joinpath(current_folder, "packing_result.json")
    open(file_path, "w") do io
        write(io, JSON.json(packing_result))
    end
    if packing_result["Success"]
        robots = [agent for agent in allagents(model) if agent isa RobotAgent]

        # Verificar si hay robots disponibles
        if isempty(robots)
            println("No hay robots disponibles en el modelo.")
            return
        end
        box_id = 1
        robot_index = 1
        start_x = 1
        start_z = 120
        # Agregar cajas al modelo
        for item in packing_result["data"]["fitItem"]
            end_pos = Tuple(item["position"])
            dimensions = Tuple(item["WHD"])
            weight = item["weight"]
            # Asignar posición inicial 
            start_pos = (start_x, Int(floor(dimensions[3]/2)), start_z)
            if item["name"] != "corner"
                box = add_agent!(BoxAgent,
                    model;
                    id = box_id,
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
                start_x = start_x + box.height + 7
                if start_x > 200
                    start_x = 1
                    start_z += 15
                end
                box_id += 1
                println("1 caja agregada")
            end
        end

        println("Cajas agregadas al modelo después de ordenarlas.")
    else
        println("Error al ordenar las cajas: ", packing_result["Reason"])
    end
    
end


function warehouse_simulation(; grid_dims = (200,50,200), num_boxes = 5)
    container = Dict(:name => "Container1", :WHD => (64, 44, 40), :weight => 3000, :corner => 0, :openTop => [1,2])
    items = [
    Dict(:name => "Box1", :WHD => [14,14,14], :weight => 5, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box2", :WHD => [10,10,10], :weight => 10, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 2, :type => 1),
    Dict(:name => "Box3", :WHD => [5,5,5], :weight => 2, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box4", :WHD => [14,14,14], :weight => 8, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box5", :WHD => [10,10,10], :weight => 6, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box6", :WHD => [5,5,5], :weight => 3, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box7", :WHD => [14,14,14], :weight => 25, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box8", :WHD => [5,5,5], :weight => 5, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box9", :WHD => [10,10,10], :weight => 10, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box10", :WHD => [14,14,14], :weight => 23, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box11", :WHD => [5,5,5], :weight => 20, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box12", :WHD => [14,14,14], :weight => 12, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box13", :WHD => [10,10,10], :weight => 6, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box14", :WHD => [5,5,5], :weight => 8, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    Dict(:name => "Box15", :WHD => [5,5,5], :weight => 9, :count => 1, :level => 1, :loadbear => 10, :updown => 1, :color => 1, :type => 1),
    ]
    space = GridSpace((200, 50, 200); periodic = false, metric = :chebyshev)
    model = StandardABM(Union{RobotAgent, BoxAgent}, space; agent_step! = agent_step!, scheduler = Schedulers.Randomly(), properties = Dict{Symbol, Any}(:matrix => nothing))
    initialize_robots!(model)
    handle_packing("http://192.168.1.85:5050/calPacking", container, items, model)
    return model
end

# Inicializa los robots y define los límites de cada uno en el almacén
function initialize_robots!(model)
    x = 20
    z = 1
    add_agent!(RobotAgent, model; id = 30, pos = (x,1,z), min_x = 5, max_x = 20, drop_zone_x = 40,drop_zone_z = 40, collect_zone_z = 100, previous_pos = (x,1,z))
    add_agent!(RobotAgent, model; id = 31, pos = (x,1,z + 40), min_x = 5, max_x = 20, drop_zone_x = 40,drop_zone_z = 40, collect_zone_z = 100, previous_pos = (x,1,z))
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
