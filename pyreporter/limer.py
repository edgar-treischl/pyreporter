import os
import requests

from dotenv import load_dotenv
import base64
import pandas as pd
from io import StringIO


load_dotenv()

def limer_connect():
    """
    Connect to LimeSurvey.

    Returns
    -------
    str
        Session ID
    """
    user = os.getenv("LIME_USERNAME")
    credential = os.getenv("LIME_PASSWORD")
    api_url = os.getenv("LIME_API_URL")

    if not all([user, credential, api_url]):
        raise RuntimeError(
            "Missing LimeSurvey credentials. "
            "Check your .env file for LIME_USERNAME, LIME_PASSWORD, and LIME_API_URL."
        )

    # Store config globally or pass explicitly (choose one style)
    os.environ["LIME_API_URL"] = api_url
    os.environ["LIME_USERNAME"] = user
    os.environ["LIME_PASSWORD"] = credential

    session = limer_sessionkey()

    # Check for invalid user
    if session == "Invalid user name or password":
        raise RuntimeError(
            "Error in limer_connect(): Invalid user name or password."
        )

    return session




# Simple module-level cache to store the session key
class SessionCache:
    session_key = None

session_cache = SessionCache()


def limer_sessionkey(
    username=None,
    password=None
):
    """
    Get LimeSurvey API Session Key

    Logs into the LimeSurvey API and returns an access session key.

    Parameters
    ----------
    username : str, optional
        LimeSurvey username. Defaults to environment variable LIME_USERNAME.
    password : str, optional
        LimeSurvey password. Defaults to environment variable LIME_PASSWORD.

    Returns
    -------
    str
        API session key
    """

    if username is None:
        username = os.getenv("LIME_USERNAME")
    if password is None:
        password = os.getenv("LIME_PASSWORD")

    api_url = os.getenv("LIME_API_URL")

    body_json = {
        "method": "get_session_key",
        "id": " ",
        "params": {
            "username": username,
            "password": password
        }
    }

    response = requests.post(
        api_url,
        json=body_json,
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()

    data = response.json()
    session_key = str(data.get("result"))

    # Store session key in cache so other functions can access it
    session_cache.session_key = session_key

    return session_key





def limer_call(method, params=None, **request_kwargs):
    """
    Make a call to the LimeSurvey API.

    Parameters
    ----------
    method : str
        API method to call (e.g. "list_surveys").
    params : dict, optional
        Parameters to pass to the API method.
    **request_kwargs
        Additional keyword arguments passed to requests.post().

    Returns
    -------
    Any
        Result returned by the API (may be plain text, dict, list, etc.).
    """

    if params is None:
        params = {}

    if not isinstance(params, dict):
        raise TypeError("params must be a dict.")

    # Ensure we have a session key
    if not session_cache.session_key:
        raise RuntimeError(
            "You need to get a session key first. Run limer_sessionkey()."
        )

    api_url = os.getenv("LIME_API_URL")
    if not api_url:
        raise RuntimeError("LIME_API_URL is not set.")

    # Merge session key with provided params
    params_full = {
        "sSessionKey": session_cache.session_key,
        **params
    }

    body_json = {
        "method": method,
        "id": " ",
        "params": params_full
    }

    response = requests.post(
        api_url,
        json=body_json,
        headers={"Content-Type": "application/json"},
        **request_kwargs
    )
    response.raise_for_status()

    data = response.json()
    return data.get("result")





def limer_list_surveys():
    """
    List surveys from LimeSurvey.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the list of surveys from LimeSurvey.
    """
    # Connect to LimeSurvey
    session = limer_connect()

    try:
        # Get data
        df = limer_call(method="list_surveys")
    finally:
        # Always release the session, even if something goes wrong
        limer_release()

    return df










import base64
import pandas as pd
from io import StringIO

def limer_responses(
    iSurveyID,
    sDocumentType="csv",
    sLanguageCode="",
    sCompletionStatus="complete",
    sHeadingType="code",
    sResponseType="long",
    **kwargs
):
    """
    Get LimeSurvey survey responses as a pandas DataFrame.
    Uses an empty string for language code to retrieve data without checking language.
    """

    # Build parameters for export_responses
    params = {
        "iSurveyID": iSurveyID,
        "sDocumentType": sDocumentType,
        "sLanguageCode": sLanguageCode,  # always ""
        "sCompletionStatus": sCompletionStatus,
        "sHeadingType": sHeadingType,
        "sResponseType": sResponseType,
    }
    params.update(kwargs)

    # Call export_responses
    results = limer_call(method="export_responses", params=params)

    # Flatten result (API usually returns dict with one key)
    if isinstance(results, dict):
        results_flat = next(iter(results.values()))
    elif isinstance(results, list) and len(results) == 1:
        results_flat = results[0]
    else:
        results_flat = results

    if not isinstance(results_flat, str):
        raise RuntimeError(f"export_responses returned non-string data: {results_flat}")

    # Decode base64 CSV
    try:
        decoded_bytes = base64.b64decode(results_flat)
    except Exception:
        raise RuntimeError(f"export_responses returned non-base64 data:\n{results_flat}")

    # Convert CSV to pandas DataFrame
    raw_csv = decoded_bytes.decode("utf-8", errors="replace")
    df = pd.read_csv(StringIO(raw_csv), sep=";", dtype=str)

    return df





def limer_n(id):
    """
    Get the number of completed responses of a LimeSurvey survey.

    Parameters
    ----------
    id : int
        LimeSurvey survey ID.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: 'sid' and 'completed_responses'.
    """

    # Call LimeSurvey API
    summary = limer_call(
        method="get_summary",
        params={"iSurveyID": id}
    )

    # Convert to DataFrame
    df = pd.DataFrame([summary])  # wrap in list to get a single-row DataFrame
    df["sid"] = id

    # Keep only 'sid' and 'completed_responses'
    df = df[["sid", "completed_responses"]]

    return df




def limer_SIDs(snr, ubb):
    """
    Get metadata of surveys filtered by school number and UBB flag.

    Parameters
    ----------
    snr : str
        School number (first 4 digits of survey title).
    ubb : bool
        Whether 'ubb' must appear in the survey title.

    Returns
    -------
    pd.DataFrame
        Surveys metadata with completed responses.
    """

    # Get list of all surveys
    surveys = pd.DataFrame(limer_call(method="list_surveys"))

    if surveys.empty:
        raise RuntimeError("No surveys returned from LimeSurvey.")

    # Extract first 4 digits of survey title as 'snr'
    surveys["snr"] = surveys["surveyls_title"].str[:4]

    # Filter surveys: first 4 chars numeric & 'ubb' presence matches
    surveys = surveys[
        surveys["snr"].str.match(r"^\d{4}$") &
        (surveys["surveyls_title"].str.contains("ubb") == ubb)
    ]

    # Further filter by provided SNR
    surveys = surveys[surveys["snr"] == snr]

    if surveys.empty:
        raise RuntimeError("Error in limer_SIDs(): No survey ID (SNR) found in LimeSurvey.")

    # Apply limer_n to each survey id to get completed responses
    stats_list = [limer_n(sid) for sid in surveys["sid"]]
    stats_df = pd.concat(stats_list, ignore_index=True)

    # Merge survey metadata with completed responses
    surveys = surveys.merge(stats_df, on="sid", how="left")

    # Convert completed_responses to numeric (coerce errors to NaN)
    surveys["completed_responses"] = pd.to_numeric(
        surveys["completed_responses"], errors="coerce"
    )

    # Keep only surveys with completed_responses > 0
    surveys = surveys[surveys["completed_responses"] > 0]

    if surveys.empty:
        raise RuntimeError("Error in limer_SIDs: No full responses available.")
        return False

    return surveys






def limer_release():
    """
    Release a LimeSurvey session key.

    Clears the LimeSurvey API session key currently in use, effectively logging out.
    """
    limer_call(method="release_session_key")

