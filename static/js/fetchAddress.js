"use-strict";

const province_select = document.getElementById("id_province");
let province_last_value;

const district_select = document.getElementById("id_district");
let district_last_value;

const municipality_select = document.getElementById("id_municipality");
let municipality_last_value;


const helper = async (base_name, fetch_name, cause, effect, last_value, callback) => {
    const cause_id = cause.value;
    if (cause_id === "") return;

    const raw_response = await fetch(`/api/address/${base_name}/${cause_id}/${fetch_name}`);
    const response = await raw_response.json();
    const data = response[fetch_name];
    console.log(data)

    if (data.length) {
        const current_value = data[0][0];
        last_value = current_value;
    }

    while (effect.firstChild) {
        effect.lastChild.remove();
    }
    data.forEach(({ id, name }) => {
        const option = document.createElement("option");
        option.value = id;
        option.innerText = name;
        effect.appendChild(option);
    });
    callback && callback();
    return last_value
};

const getDistricts = async () => {
    district_last_value = await helper(
        "provinces",
        "districts",
        province_select,
        district_select,
        district_last_value,
        getMunicipalities
    );
};

const getMunicipalities = async () => {
    municipality_last_value = await helper(
        "districts",
        "municipalities",
        district_select,
        municipality_select,
        municipality_last_value,
        null
    );
};


province_select.onchange = getDistricts;
district_select.onchange = getMunicipalities;
