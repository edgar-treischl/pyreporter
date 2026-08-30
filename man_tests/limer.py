from pyreporter.limer import limer_connect, limer_list_surveys, limer_responses, limer_release, limer_n, limer_SIDs

limer_connect()

df = limer_responses(
    iSurveyID=252356,
    sCompletionStatus="complete"
)

print("\nFetch data...")
print(df.head())

print("\nFetched N:")

df_summary = limer_n(252356)
print(df_summary)

print("\nFetched SIDs:")
df_surveys = limer_SIDs(snr="0001", ubb=False)
print(df_surveys.head())

print("\nListing surveys...")
surveys = limer_list_surveys()
print(surveys[:5])

limer_release()
