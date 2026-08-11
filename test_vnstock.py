from vnstock import Reference
df = Reference().company.info("FPT")
print("Data fetch successful:", not df.empty)
