from .entso_data_converter import ENTSODataConverter
from .add_residual_mix import add_swiss_residual_mix
import bw2data as bd
import bw_processing as bwp
from fs.zipfs import ZipFS
from pathlib import Path
from bentso.constants import ENTSO_COUNTRIES
from tqdm import tqdm
import numpy as np

DATA_DIR = Path(__file__).parent.parent.resolve() / "data"


def create_average_entso_datapackages():
    bd.projects.set_current("GSA for archetypes")
    add_swiss_residual_mix()

    dc = ENTSODataConverter("ecoinvent 3.8 cutoff")

    # Start with average datapackages
    dp = bwp.create_datapackage(
        fs=ZipFS(str(DATA_DIR / "entso-average.zip"), write=True),
        name="Average ENTSO generation and trade",
        # set seed to have reproducible (though not sequential) sampling
        seed=42,
    )

    indices, data = [], []

    for country in tqdm(ENTSO_COUNTRIES):
        if country in ("LU", "MT", "MK"):
            continue

        tqdm.write(country)

        hv = dc.data_dict_for_high_voltage_market(country, years=(2019, 2020, 2021))
        keys = sorted(hv)

        indices.append(np.array([(x, y) for x, y, _ in keys], dtype=bwp.INDICES_DTYPE))
        data.append(np.array([hv[key].fillna(0).mean() for key in keys]))

        mv = dc.data_dict_for_medium_voltage_market(country, years=(2019, 2020, 2021))
        keys = sorted(mv)

        indices.append(np.array([(x, y) for x, y, _ in keys], dtype=bwp.INDICES_DTYPE))
        data.append(np.array([mv[key].fillna(0).mean() for key in keys]))

        lv = dc.data_dict_for_low_voltage_market(country, years=(2019, 2020, 2021))
        keys = sorted(lv)

        indices.append(np.array([(x, y) for x, y, _ in keys], dtype=bwp.INDICES_DTYPE))
        data.append(np.array([lv[key].fillna(0).mean() for key in keys]))

    data = np.hstack(data)

    dp.add_persistent_vector(
        matrix="technosphere_matrix",
        data_array=data,
        # Resource group name that will show up in provenance
        name="average ENTSO electricity values",
        indices_array=np.hstack(indices),
        flip_array=np.ones(len(data), dtype=bool),
    )
    dp.finalize_serialization()


def create_timeseries_entso_datapackages():
    bd.projects.set_current("GSA for archetypes")
    add_swiss_residual_mix()

    dc = ENTSODataConverter("ecoinvent 3.8 cutoff")

    # Start with average datapackages
    dp = bwp.create_datapackage(
        fs=ZipFS(str(DATA_DIR / "entso-timeseries.zip"), write=True),
        name="2019-2021 ENTSO generation and trade timeseries",
        # set seed to have reproducible (though not sequential) sampling
        seed=42,
    )

    indices, data = [], []

    for country in tqdm(sorted(ENTSO_COUNTRIES)):
        if country in ("LU", "MT", "MK"):
            continue

        tqdm.write(country)

        hv = dc.data_dict_for_high_voltage_market(country, years=(2019, 2020, 2021))
        keys = sorted(hv)

        indices.append(np.array([(x, y) for x, y, _ in keys], dtype=bwp.INDICES_DTYPE))
        data.append(np.array([hv[key].fillna(0) for key in keys]))

        mv = dc.data_dict_for_medium_voltage_market(country, years=(2019, 2020, 2021))
        keys = sorted(mv)

        indices.append(np.array([(x, y) for x, y, _ in keys], dtype=bwp.INDICES_DTYPE))
        data.append(np.array([mv[key].fillna(0) for key in keys]))

        lv = dc.data_dict_for_low_voltage_market(country, years=(2019, 2020, 2021))
        keys = sorted(lv)

        indices.append(np.array([(x, y) for x, y, _ in keys], dtype=bwp.INDICES_DTYPE))
        data.append(np.array([lv[key].fillna(0) for key in keys]))

    min_hours = min(arr.shape[1] for arr in data)
    data = [arr[:, :min_hours] for arr in data]

    data = np.vstack(data)

    dp.add_persistent_array(
        matrix="technosphere_matrix",
        data_array=data,
        # Resource group name that will show up in provenance
        name="timeseries ENTSO electricity values",
        indices_array=np.hstack(indices),
        flip_array=np.ones(len(data), dtype=bool),
    )
    dp.finalize_serialization()
